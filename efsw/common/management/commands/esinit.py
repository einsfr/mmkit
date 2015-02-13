import os
import optparse

from django.core.management import base
from django.conf import settings

from efsw.common.search import elastic


class Command(base.BaseCommand):

    option_list = base.BaseCommand.option_list + (
        optparse.make_option(
            '--replace',
            action='store_true',
            dest='replace',
            default=False
        ),
    )

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        es = elastic.get_es()
        init_indices = getattr(settings, 'EFSW_ELASTIC_INIT_INDICES', ())
        if not init_indices:
            if verbosity:
                print('Список индексов для инициализации пустой - пропускаем')
            return
        if verbosity:
            print('Обработка списка индексов:')
        count = 0
        for ind in init_indices:
            if not os.path.exists(ind):
                raise FileNotFoundError(
                    'Файл (папка) с индексом для инициализации поиска не существует: {0}'.format(ind)
                )
            if os.path.isfile(ind) and self._compatible(ind):
                self._create_index(es, ind, options['replace'], verbosity)
                count += 1
            elif os.path.isdir(ind):
                if verbosity >= 2:
                    print('  {0}'.format(ind))
                for p in os.listdir(ind):
                    full_path = os.path.join(ind, p)
                    if os.path.isfile(full_path) and self._compatible(full_path):
                        self._create_index(es, full_path, options['replace'], verbosity)
                        count += 1
        if verbosity:
            print('Загрузка индексов для инициализации завершена. Всего загружено: {0}'.format(count))


    def _create_index(self, es, path, replace, verbosity):
        index_name = os.path.splitext(os.path.basename(path))[0]
        if verbosity >= 2:
            print('    {0} - {1}'.format(index_name, path))
        if es.indices.exists(index_name):
            if replace:
                if verbosity >= 2:
                    print('    Индекс существует - заменяю')
                es.indices.delete(index_name)
            else:
                if verbosity >= 2:
                    print('    Индекс существует - пропускаю')
                return
        with open(path, 'r') as f:
            es.indices.create(index=index_name, body=f.read())

    def _compatible(self, path):
        return os.path.splitext(os.path.basename(path))[1] == '.json'