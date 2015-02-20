import json

from efsw.common.search import models, elastic


def create_model_index_doc(instance: models.IndexableModel):
    es_cm = elastic.get_connection_manager()
    es_cm.get_es().create(
        '{0}{1}'.format(es_cm.get_es_index_prefix(), instance.get_index_name()),
        instance.get_doc_type(),
        json.dumps(
            instance.get_doc_body()
        ),
        id=instance.id
    )


def update_model_index_doc(instance: models.IndexableModel):
    es_cm = elastic.get_connection_manager()
    es_cm.get_es().update(
        '{0}{1}'.format(es_cm.get_es_index_prefix(), instance.get_index_name()),
        instance.get_doc_type(),
        instance.id,
        json.dumps({'doc': instance.get_doc_body()})
    )


def delete_model_index_doc(instance: models.IndexableModel):
    es_cm = elastic.get_connection_manager()
    es_cm.get_es().delete(
        '{0}{1}'.format(es_cm.get_es_index_prefix(), instance.get_index_name()),
        instance.get_doc_type(),
        instance.id
    )