import json

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
        es_cm = elastic.get_connection_manager()
        es = es_cm.get_es()
        index_name = '{0}{1}'.format(es_cm.get_es_index_prefix(), instance.get_index_name())
        if created:
            es.create(
                index_name,
                instance.get_doc_type(),
                json.dumps(
                    instance.get_doc_body()
                ),
                id=instance.id
            )
        else:
            try:
                es.update(
                    index_name,
                    instance.get_doc_type(),
                    instance.id,
                    json.dumps({'doc': instance.get_doc_body()})
                )
            except EsNotFoundError:
                # TODO: Добавить запись в лог в debug-режиме
                es.create(
                    index_name,
                    instance.get_doc_type(),
                    json.dumps(
                        instance.get_doc_body()
                    ),
                    id=instance.id
                )


@receiver(signals.post_delete)
def model_deleted(sender, instance, *args, **kwargs):
    if isinstance(instance, IndexableModel)\
            and not getattr(settings, "EFSW_ELASTIC_DISABLE", default_settings.EFSW_ELASTIC_DISABLE):
        es_cm = elastic.get_connection_manager()
        es = es_cm.get_es()
        es.delete(
            '{0}{1}'.format(es_cm.get_es_index_prefix(), instance.get_index_name()),
            instance.get_doc_type(),
            instance.id
        )