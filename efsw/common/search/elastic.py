import elasticsearch
import json
import time

from django.conf import settings

from efsw.common.search import exceptions
from efsw.common.search.models import IndexableModel
from efsw.common import default_settings as common_default_settings


es_instance = None

es_instance_timestamp = None


def _get_es_instance():
    try:
        es_hosts = getattr(settings, 'EFSW_ELASTIC_HOSTS')
    except AttributeError:
        raise exceptions.EsConfigException('Ошибка конфигурации: отсутствует параметр EFSW_ELASTIC_HOSTS (список '
                                           'хостов, используемых ES)')

    es_options = getattr(settings, 'EFSW_ELASTIC_OPTIONS', {})
    global es_instance_timestamp
    es_instance_timestamp = time.time()
    return elasticsearch.Elasticsearch(es_hosts, **es_options)


def get_es():
    global es_instance
    global es_instance_timestamp
    if es_instance is None:
        es_instance = _get_es_instance()
    else:
        max_time_delta = getattr(
            settings,
            'EFSW_ELASTIC_CHECK_INTERVAL',
            common_default_settings.EFSW_ELASTIC_CHECK_INTERVAL
        )
        if time.time() - es_instance_timestamp >= max_time_delta >= 0:
            es_instance = _get_es_instance()

    return es_instance


def create_document(model: IndexableModel):
    es = get_es()
    es.create(model.get_index_name(), model.get_doc_type(), json.dumps(model.get_doc_body()), id=model.id)


def update_document(model: IndexableModel):
    es = get_es()
    doc_body = {'doc': model.get_doc_body()}
    es.update(model.get_index_name(), model.get_doc_type(), model.id, json.dumps(doc_body))


def delete_document(model: IndexableModel):
    es = get_es()
    es.delete(model.get_index_name(), model.get_doc_type(), model.id)