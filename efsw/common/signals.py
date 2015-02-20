import json

from django.dispatch import receiver
from django.db.models import signals

from elasticsearch.exceptions import NotFoundError as EsNotFoundError

from efsw.common.search.models import IndexableModel
from efsw.common.search import elastic, shortcuts as es_shortcuts


@receiver(signals.post_save)
def model_saved(sender, instance, created, raw, *args, **kwargs):
    if isinstance(instance, IndexableModel) and elastic.es_enabled():
        if created:
            es_shortcuts.create_model_index_doc(instance)
        else:
            try:
                es_shortcuts.update_model_index_doc(instance)
            except EsNotFoundError:
                # TODO: Добавить запись в лог в debug-режиме
                es_shortcuts.create_model_index_doc(instance)


@receiver(signals.post_delete)
def model_deleted(sender, instance, *args, **kwargs):
    if isinstance(instance, IndexableModel) and elastic.es_enabled():
        es_shortcuts.delete_model_index_doc(instance)