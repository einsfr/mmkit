import uuid

from django.db import models
from django.contrib.postgres.fields import HStoreField


class AbstractStorage(models.Model):

    class Meta:
        app_label = 'common'
        abstract = True

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        verbose_name='имя',
        max_length=255
    )


class MetaStorage(AbstractStorage):

    class Meta:
        app_label = 'common'
        verbose_name = 'хранилище метаданных'
        verbose_name_plural = 'хранилища метаданных'


class FileStorage(AbstractStorage):

    class Meta:
        app_label = 'common'
        verbose_name = 'файловое хранилище'
        verbose_name_plural = 'файловые хранилища'

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


class AbstractStorageObject(models.Model):

    class Meta:
        app_label = 'common'
        abstract = True

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )


class FileStorageObject(AbstractStorageObject):

    class Meta:
        app_label = 'common'
        verbose_name = 'объект в файловом хранилище'
        verbose_name_plural = 'объекты в файловом хранилище'

    storage = models.ForeignKey(
        FileStorage,
        related_name='stored_objects'
    )

    path = models.CharField(
        max_length=255,
        verbose_name='путь к объекту'
    )


class MetaStorageObject(AbstractStorageObject):

    class Meta:
        app_label = 'common'
        verbose_name = 'объект в хранилище метаданных'
        verbose_name_plural = 'объекты в хранилище метаданных'

    storage = models.ForeignKey(
        MetaStorage,
        related_name='stored_objects'
    )

    location = models.CharField(
        max_length=255,
        verbose_name='место хранения объекта'
    )
