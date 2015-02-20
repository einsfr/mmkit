import json

from django.core.management import base
from django.apps import apps

from elasticsearch import helpers

from efsw.common.search import elastic, models


class Command(base.BaseCommand):

    def handle(self, *models_classes_list, **options):
        verbosity = int(options['verbosity'])
        if not models_classes_list:
            if verbosity:
                print('Список классов не передан - использую все доступные приложению модели')
            models_classes_list = [x for x in apps.get_models() if issubclass(x, models.IndexableModel)]
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
        count = 0
        for mc in models_classes_list:
            index_name = es_cm.prefix_index_name(mc.get_index_name())
            if index_name not in exist_index_names:
                if verbosity:
                    print('  {0} {1}: Индекс не существует - пропускаю'.format(index_name, mc))
                continue
            model_objects = list(mc.objects.all())
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
            count += result[0]
        if verbosity:
            print('Завершено')
            print('Всего проиндексировано моделей: {0}; в них объектов: {1}'.format(
                len(models_classes_list), count
            ))