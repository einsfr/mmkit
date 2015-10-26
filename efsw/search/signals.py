from django.dispatch import receiver
from django.db.models import signals

from efsw.search.models import IndexableModel
from efsw.search import elastic, shortcuts as es_shortcuts


@receiver(signals.post_save)
def model_saved(sender, instance, created, raw, *args, **kwargs):
    if isinstance(instance, IndexableModel) and elastic.es_enabled():
        if created:
            es_shortcuts.create_model_index_doc(instance)
        else:
            es_shortcuts.update_model_index_doc(instance)


@receiver(signals.post_delete)
def model_deleted(sender, instance, *args, **kwargs):
    if isinstance(instance, IndexableModel) and elastic.es_enabled():
        es_shortcuts.delete_model_index_doc(instance)