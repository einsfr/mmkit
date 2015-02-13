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
        index_name = getattr(settings, 'EFSW_ELASTIC_INDEX')
        if es.indices.exists(index_name):
            if options['replace']:
                es.indices.delete(index_name)
            else:
                raise elastic.exceptions.EsIndexExistsException(index_name)
        es.indices.create(index_name)
        init_mappings = getattr(settings, 'EFSW_ELASTIC_INIT_MAPPINGS', ())
        if not init_mappings:
            if verbosity:
                print('Список типов для инициализации пустой - пропускаем.')
            return
        if verbosity:
            print('Обработка списка типов:')
        count = 0
        for im in init_mappings:
            if not os.path.exists(im):
                raise FileNotFoundError('Файл (папка) с типами для инициализации поиска не существует: {0}'.format(im))
            if os.path.isfile(im) and self._compatible(im):
                self._load_mappings(es, index_name, im, verbosity)
                count += 1
            elif os.path.isdir(im):
                if verbosity >= 2:
                    print('  {0}'.format(im))
                for p in os.listdir(im):
                    full_path = os.path.join(im, p)
                    if os.path.isfile(full_path) and self._compatible(full_path):
                        self._load_mappings(es, index_name, full_path, verbosity)
                        count += 1

        if verbosity:
            print('Загрузка типов для инициализации завершена. Всего загружено: {0}'.format(count))

    def _load_mappings(self, es, index_name, path, verbosity):
        type_name = os.path.splitext(os.path.basename(path))[0]
        if verbosity >= 2:
            print('    {0} - {1}'.format(type_name, path))
        with open(path, 'r') as f:
            es.indices.put_mapping(index=index_name, doc_type=type_name, body=f.read())

    def _compatible(self, path):
        return os.path.splitext(os.path.basename(path))[1] == '.json'