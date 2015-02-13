import elasticsearch

from django.conf import settings

from efsw.common.search import exceptions


es_instance = None


def _get_es_instance():
    try:
        es_hosts = getattr(settings, 'EFSW_ELASTIC_HOSTS')
    except AttributeError:
        raise exceptions.EsConfigException('Ошибка конфигурации: отсутствует параметр EFSW_ELASTIC_HOSTS (список '
                                           'хостов, используемых ES)')

    es_options = getattr(settings, 'EFSW_ELASTIC_OPTIONS', {})
    return elasticsearch.Elasticsearch(es_hosts, **es_options)


def get_es():
    global es_instance
    if es_instance is None:
        es_instance = _get_es_instance()

    return es_instance