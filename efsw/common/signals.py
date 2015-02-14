from django.dispatch import receiver
from django.db.models import signals

from efsw.common.search.models import IndexableModel
from efsw.common.search import elastic


@receiver(signals.post_save)
def model_saved(sender, instance, created, raw, *args, **kwargs):
    if isinstance(instance, IndexableModel):
        if created:
            elastic.create_document(instance)
        else:
            elastic.update_document(instance)


@receiver(signals.post_delete)
def model_deleted(sender, instance, *args, **kwargs):
    if isinstance(instance, IndexableModel):
        elastic.delete_document(instance)