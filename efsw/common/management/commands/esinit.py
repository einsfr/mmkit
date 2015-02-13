from django.core.management import base
from django.conf import settings

import optparse

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
        es = elastic.get_es()
        index_name = getattr(settings, 'EFSW_ELASTIC_INDEX')
        if es.indices.exists(index_name):
            if options['replace']:
                es.indices.delete(index_name)
            else:
                raise elastic.exceptions.EsIndexExistsException(index_name)
        es.indices.create(index_name)
        # Потом - пробежаться по всем установленным приложениям в поисках файла, определяющего mapping'и и создать их