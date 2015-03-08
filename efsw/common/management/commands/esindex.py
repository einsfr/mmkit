import json

from django.core.management import base
from django.apps import apps
from django.db.utils import OperationalError

from elasticsearch import helpers

from efsw.common.search import elastic, models


class Command(base.BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('models_list', nargs='*')

    def handle(self, *args, **options):
        verbosity = int(options['verbosity'])
        models_list = options['models_list']
        if not models_list:
            if verbosity:
                print('Список классов не передан - использую все доступные приложению модели')
            models_classes_list = [x for x in apps.get_models() if issubclass(x, models.IndexableModel)]
        else:
            models_classes_list = []
            for model_name in models_list:
                try:
                    model_class = apps.get_model(model_name)
                except LookupError:
                    if verbosity:
                        print('Невозможно найти модель "{0}" - пропускаю'.format(model_name))
                    continue
                if issubclass(model_class, models.IndexableModel):
                    models_classes_list.append(model_class)
        if not models_classes_list:
            if verbosity:
                print('В списке классов нет ни одного, доступного для индексации - выполнение прекращено.')
            return
        es_cm = elastic.get_connection_manager()
        index_names = [es_cm.prefix_index_name(x.get_index_name()) for x in models_classes_list]
        if verbosity >= 2:
            print('Индексы, используемые моделями:')
            print(index_names)
        es = es_cm.get_es()
        exist_index_names = list(filter(es.indices.exists, index_names))
        if verbosity >= 2:
            print('Существующие индексы:')
            print(exist_index_names)
        exist_index_count = len(exist_index_names)
        if not exist_index_count:
            if verbosity:
                print('Не существует ни одного индекса для моделей - возможно, необходимо запустить команду esinit '
                      'перед запуском индексации?')
            return
        if verbosity and (len(index_names) != len(exist_index_names)):
            print('Не все модели имеют существующие индексы - возможно, необходимо запустить команду esinit перед '
                  'запуском индексации?')
        if verbosity:
            print('Очищаю индексы...')
        es.delete_by_query(exist_index_names, body=json.dumps({'query': {'match_all': {}}}))
        if verbosity:
            print('Завершено')
            print('Начинаю индексацию...')
        obj_count = 0
        mod_count = 0
        for mc in models_classes_list:
            index_name = es_cm.prefix_index_name(mc.get_index_name())
            if index_name not in exist_index_names:
                if verbosity:
                    print('  {0} {1}: Индекс не существует - пропускаю'.format(index_name, mc))
                continue
            try:
                model_objects = list(mc.objects.all())
            except OperationalError:
                if verbosity:
                    print('  {0}: Ошибка получения объектов - возможно, таблица не существует?'.format(mc))
                continue
            if verbosity >= 2:
                print('  {0}: Найдено {1} объектов'.format(mc, len(model_objects)))
            if not model_objects:
                if verbosity:
                    print('  {0}: Объекты отсутствуют - пропускаю'.format(mc))
                continue
            bulk_actions = [
                {
                    '_index': index_name,
                    '_type': mc.get_doc_type(),
                    '_id': x.id,
                    '_source': json.dumps(x.get_doc_body())
                }
                for x in model_objects
            ]
            result = helpers.bulk(es, bulk_actions, refresh=True)
            if verbosity >= 2:
                print('    Из них проиндексировано: {0}'.format(result[0]))
            if verbosity and result[0] != len(model_objects):
                print('    При индексировании объектов модели произошли ошибки: {0}'.format(result[1]))
            obj_count += result[0]
            mod_count += 1
        if verbosity:
            print('Завершено')
            print('Всего успешно проиндексировано моделей: {0}; в них объектов: {1}'.format(
                mod_count, obj_count
            ))