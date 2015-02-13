from django.core.management import base
from django.conf import settings

from efsw.common.search import elastic


class Command(base.BaseCommand):

    def handle(self, *args, **options):
        es = elastic.get_es()
        index_name = getattr(settings, 'EFSW_ELASTIC_INDEX')
        if es.indices.exists(index_name):  # удалять нужно только если есть опция на удаление существующего, или ошибка
            es.indices.delete(index_name, ignore=404)
        es.indices.create(index_name)
        # Потом - пробежаться по всем установленным приложениям в поисках файла, определяющего mapping'и и создать их