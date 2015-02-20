import elasticsearch
import time

from django.conf import settings

from efsw.common.search import exceptions
from efsw.common import default_settings as common_default_settings


_es_cm_instance = None


def get_connection_manager():
    global _es_cm_instance
    if _es_cm_instance is None:
        _es_cm_instance = EsConnectionManager()
    return _es_cm_instance


def es_enabled():
    return not getattr(settings, 'EFSW_ELASTIC_DISABLE', common_default_settings.EFSW_ELASTIC_DISABLE)


class EsConnectionManager():

    def __init__(self):
        self._es_instance = None
        self._es_instance_timestamp = None
        self._es_instance_status = None
        self._es_index_prefix = None

    def _set_es_instance(self):
        try:
            es_hosts = getattr(settings, 'EFSW_ELASTIC_HOSTS')
        except AttributeError:
            raise exceptions.EsConfigException('Ошибка конфигурации: отсутствует параметр EFSW_ELASTIC_HOSTS (список '
                                               'хостов, используемых ES)')

        es_options = getattr(settings, 'EFSW_ELASTIC_OPTIONS', {})
        self._es_instance_timestamp = time.time()
        self._es_instance = elasticsearch.Elasticsearch(es_hosts, **es_options)
        self._set_es_status()

    def _set_es_status(self):
        if self._es_instance is None:
            self._es_instance_status = None
        else:
            try:
                self._es_instance_status = str(self._es_instance.cluster.health()['status']).lower()
            except elasticsearch.ConnectionError:
                self._es_instance_status = None

    def get_es(self):
        if not es_enabled():
            self._es_instance = None
            self._es_instance_status = None
            self._es_instance_timestamp = None
            return None
        if self._es_instance is None:
            if self._es_instance_timestamp is None:
                # Если ещё не было попыток создания
                self._set_es_instance()
            else:
                # Если уже были
                err_check_int = getattr(
                    settings,
                    'EFSW_ELASTIC_ERROR_CHECK_INTERVAL',
                    common_default_settings.EFSW_ELASTIC_ERROR_CHECK_INTERVAL
                )
                if time.time() - self._es_instance_timestamp >= err_check_int >= 0:
                    self._set_es_instance()
                else:
                    return None
        else:
            max_time_delta = getattr(
                settings,
                'EFSW_ELASTIC_CHECK_INTERVAL',
                common_default_settings.EFSW_ELASTIC_CHECK_INTERVAL
            )
            if time.time() - self._es_instance_timestamp >= max_time_delta >= 0:
                self._set_es_instance()

        return self._es_instance

    def get_es_status(self):
        return self._es_instance_status

    def get_es_index_prefix(self):
        if self._es_index_prefix is None:
            self._es_index_prefix = getattr(
                settings,
                'EFSW_ELASTIC_INDEX_PREFIX',
                common_default_settings.EFSW_ELASTIC_INDEX_PREFIX
            )
        return self._es_index_prefix
