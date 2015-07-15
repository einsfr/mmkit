import uuid
import os

from django.db import models
from django.contrib.postgres.fields import HStoreField, ArrayField
from django.conf import settings

from efsw.common.utils import urlformatter


class FileStorage(models.Model):

    class Meta:
        app_label = 'common'
        verbose_name = 'файловое хранилище'
        verbose_name_plural = 'файловые хранилища'

    def __str__(self):
        return self.name

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

    def get_url(self, fs_object, protocol=None):
        if protocol is not None:
            try:
                base_url = self.access_protocols[protocol]
            except KeyError:
                return None
            return urlformatter.format_url('{0}/{1}'.format(base_url, fs_object.path)),
        else:
            return (
                urlformatter.format_url('{0}/{1}'.format(base_url, fs_object.path))
                for p, base_url in self.access_protocols.items()
            )

    def get_path(self, fs_object):
        return os.path.normpath(os.path.join(
            settings.EFSW_STORAGE_ROOT,
            self.base_dir,
            fs_object.path
        ))

    def get_or_create_file_object(self, path):
        try:
            file_object = self.stored_objects.get(path__iexact=path)
        except FileStorageObject.DoesNotExist:
            file_object = FileStorageObject(
                path=path,
                storage=self
            )
            file_object.save()
        except FileStorageObject.MultipleObjectsReturned:
            raise  # TODO: здесь должно быть удаление лишнего и каскад по связанным моделям
        return file_object


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
        verbose_name='путь к объекту',
        unique=True,
    )

    def get_url(self, protocol=None):
        return self.storage.get_url(self, protocol)

    def get_path(self):
        return self.storage.get_path(self)
