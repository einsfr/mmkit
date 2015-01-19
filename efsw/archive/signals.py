from django.dispatch import receiver
from django.db.models import signals
from django.utils import timezone

from efsw.archive import models


@receiver(signals.post_save, sender=models.Item)
def log_on_item_save(sender, instance, created, raw, *args, **kwargs):
    """ Добавление записи в журнал после сохранения модели Item """

    if not raw:
        il = models.ItemLog()
        il.item = instance
        il.dt = timezone.now()
        if created:
            il.action = il.ACTION_ADD
        else:
            il.action = il.ACTION_UPDATE
        il.save()


@receiver(signals.post_save, sender=models.Item)
def create_default_dir_on_item_create(sender, instance, created, raw, *args, **kwargs):
    """ Добавление папки по-умолчанию элементу при создании """

    if created and not raw:
        fo = models.ItemFolder()
        fo.item = instance
        fo.name = fo.DEFAULT_FOLDER_NAME
        fo.save()