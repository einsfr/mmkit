import os

from django.dispatch import receiver
from django.db.models import signals
from django.utils import timezone
from django.conf import settings

from efsw.archive import models
from efsw.archive import default_settings
from efsw.archive import exceptions


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


@receiver(signals.m2m_changed, sender=models.Item.includes.through)
def log_on_item_includes_change(sender, instance, action, pk_set, *args, **kwargs):
    """ Добавление записи в журнал после изменения связей между моделями Item """

    if action not in ['post_add', 'post_remove']:
        return
    il = models.ItemLog()
    il.item = instance
    il.dt = timezone.now()
    il.action = il.ACTION_INCLUDE_UPDATE
    il.save()
    for pk in pk_set:
        try:
            item = models.Item.objects.get(pk=pk)
        except models.Item.DoesNotExist:
            continue
        il_rev = models.ItemLog()
        il_rev.item = item
        il_rev.dt = timezone.now()
        il_rev.action = il_rev.ACTION_INCLUDE_UPDATE
        il_rev.save()


@receiver(signals.post_save, sender=models.Item)
def fs_ops_on_folder_create(sender, instance, created, raw, *args, **kwargs):
    """ Операции с файловой системой после создания элемента """

    if created and not getattr(settings, 'EFSW_ARCH_SKIP_FS_OPS', default_settings.EFSW_ARCH_SKIP_FS_OPS):
        storage_root = getattr(settings, 'EFSW_ARCH_STORAGE_ROOT', default_settings.EFSW_ARCH_STORAGE_ROOT)
        if not os.path.isdir(storage_root):
            raise exceptions.StorageRootNotFound()
        dir_mask = getattr(settings, 'EFSW_ARCH_DIR_MODE', default_settings.EFSW_ARCH_DIR_MODE)
        try:
            os.makedirs(instance.get_storage_path(), dir_mask)
        except:
            raise