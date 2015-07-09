import uuid

from django.db import models
from django.contrib.postgres.fields import HStoreField, ArrayField


class FileStorage(models.Model):

    class Meta:
        app_label = 'common'
        verbose_name = 'файловое хранилище'
        verbose_name_plural = 'файловые хранилища'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        verbose_name='имя',
        max_length=255
    )

    base_dir = models.CharField(
        max_length=255,
        verbose_name='корневая директория'
    )

    access_protocols = HStoreField(
        editable=False
    )

    read_only = models.BooleanField(
        verbose_name='только для чтения',
        default=True
    )

    allowed_usage = ArrayField(
        models.CharField(max_length=16)
    )


class FileStorageObject(models.Model):

    class Meta:
        app_label = 'common'
        verbose_name = 'объект в файловом хранилище'
        verbose_name_plural = 'объекты в файловом хранилище'
        unique_together = ('storage', 'id')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    storage = models.ForeignKey(
        FileStorage,
        related_name='stored_objects'
    )

    path = models.CharField(
        max_length=255,
        verbose_name='путь к объекту'
    )
