import json

from elasticsearch import NotFoundError, RequestError

from efsw.common.search import models, elastic


def create_model_index_doc(instance: models.IndexableModel):
    es_cm = elastic.get_connection_manager()
    if es_cm.get_es().exists(
        es_cm.prefix_index_name(instance.get_index_name()),
        instance.id,
        instance.get_doc_type()
    ):
        update_model_index_doc(instance)
    else:
        es_cm.get_es().create(
            es_cm.prefix_index_name(instance.get_index_name()),
            instance.get_doc_type(),
            json.dumps(
                instance.get_doc_body()
            ),
            id=instance.id
        )

def update_model_index_doc(instance: models.IndexableModel):
    es_cm = elastic.get_connection_manager()
    try:
        es_cm.get_es().update(
            es_cm.prefix_index_name(instance.get_index_name()),
            instance.get_doc_type(),
            instance.id,
            json.dumps({'doc': instance.get_doc_body()})
        )
    except NotFoundError:
        # Если модель обновилась, но индекса для неё не было - такое возможно, правда?
        create_model_index_doc(instance)
    except RequestError as exc:
        # Если индекс не хранить _source - внести в него частичные изменения не получится (по крайней мере в версии 1.4)
        if str(exc.error).startswith('DocumentSourceMissingException'):
            delete_model_index_doc(instance)
            create_model_index_doc(instance)
        else:
            raise


def delete_model_index_doc(instance: models.IndexableModel):
    es_cm = elastic.get_connection_manager()
    es_cm.get_es().delete(
        es_cm.prefix_index_name(instance.get_index_name()),
        instance.get_doc_type(),
        instance.id
    )