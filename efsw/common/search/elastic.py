import elasticsearch
import time

from django.conf import settings

from efsw.common.search import exceptions
from efsw.common import default_settings as common_default_settings


_es_instance = None

_es_instance_timestamp = None

_es_instance_status = None

_es_index_prefix = None


def _set_es_instance():
    try:
        es_hosts = getattr(settings, 'EFSW_ELASTIC_HOSTS')
    except AttributeError:
        raise exceptions.EsConfigException('Ошибка конфигурации: отсутствует параметр EFSW_ELASTIC_HOSTS (список '
                                           'хостов, используемых ES)')

    es_options = getattr(settings, 'EFSW_ELASTIC_OPTIONS', {})
    global _es_instance_timestamp
    _es_instance_timestamp = time.time()
    global _es_instance
    _es_instance = elasticsearch.Elasticsearch(es_hosts, **es_options)
    _set_es_status()


def _set_es_status():
    global _es_instance_status
    global _es_instance
    if _es_instance is None:
        _es_instance_status = None
    else:
        try:
            _es_instance_status = str(_es_instance.cluster.health()['status']).lower()
        except elasticsearch.ConnectionError:
            _es_instance_status = None


def get_es():
    global _es_instance
    global _es_instance_status
    global _es_instance_timestamp
    if getattr(settings, 'EFSW_ELASTIC_DISABLE', common_default_settings.EFSW_ELASTIC_DISABLE):
        _es_instance = None
        _es_instance_status = None
        _es_instance_timestamp = None
        return None
    if _es_instance is None:
        if _es_instance_timestamp is None:
            # Если ещё не было попыток создания
            _set_es_instance()
        else:
            # Если уже были
            err_check_int = getattr(
                settings,
                'EFSW_ELASTIC_ERROR_CHECK_INTERVAL',
                common_default_settings.EFSW_ELASTIC_ERROR_CHECK_INTERVAL
            )
            if time.time() - _es_instance_timestamp >= err_check_int >= 0:
                _set_es_instance()
            else:
                return None
    else:
        max_time_delta = getattr(
            settings,
            'EFSW_ELASTIC_CHECK_INTERVAL',
            common_default_settings.EFSW_ELASTIC_CHECK_INTERVAL
        )
        if time.time() - _es_instance_timestamp >= max_time_delta >= 0:
            _set_es_instance()

    return _es_instance


def get_es_status():
    global _es_instance_status
    return _es_instance_status


def get_es_index_prefix():
    global _es_index_prefix
    if _es_index_prefix is None:
        _es_index_prefix = getattr(
            settings,
            'EFSW_ELASTIC_INDEX_PREFIX',
            common_default_settings.EFSW_ELASTIC_INDEX_PREFIX
        )
    return _es_index_prefix