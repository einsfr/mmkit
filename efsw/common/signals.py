from django.dispatch import receiver
from django.db.models import signals
from django.conf import settings

from elasticsearch.exceptions import NotFoundError as EsNotFoundError

from efsw.common.search.models import IndexableModel
from efsw.common.search import elastic
from efsw.common import default_settings


@receiver(signals.post_save)
def model_saved(sender, instance, created, raw, *args, **kwargs):
    if isinstance(instance, IndexableModel)\
            and not getattr(settings, "EFSW_ELASTIC_DISABLE", default_settings.EFSW_ELASTIC_DISABLE):
        if created:
            elastic.create_document(instance)
        else:
            try:
                elastic.update_document(instance)
            except EsNotFoundError:
                elastic.create_document(instance)  # TODO: Добавить запись в лог в debug-режиме


@receiver(signals.post_delete)
def model_deleted(sender, instance, *args, **kwargs):
    if isinstance(instance, IndexableModel)\
            and not getattr(settings, "EFSW_ELASTIC_DISABLE", default_settings.EFSW_ELASTIC_DISABLE):
        elastic.delete_document(instance)