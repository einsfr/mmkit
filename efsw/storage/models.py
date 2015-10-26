import uuid
import os
import shutil

from django.db import models
from django.contrib.postgres.fields import HStoreField, ArrayField
from django.conf import settings

from efsw.common.utils import urlformatter
from efsw.storage.utils import in_path
from efsw.storage.exceptions import StorageRootNotFound, StorageBaseDirNotFound
from efsw.storage import errors as storage_errors


class FileStorage(models.Model):

    class Meta:
        app_label = 'storage'
        verbose_name = 'файловое хранилище'
        verbose_name_plural = 'файловые хранилища'

    def __str__(self):
        return self.name

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4
    )

    name = models.CharField(
        verbose_name='имя',
        max_length=255
    )

    base_dir = models.CharField(
        max_length=255,
        verbose_name='корневая директория',
        unique=True
    )

    access_protocols = HStoreField(
        blank=True,
        default={}
    )

    read_only = models.BooleanField(
        verbose_name='только для чтения',
        default=True
    )

    allowed_usage = ArrayField(
        models.CharField(max_length=16),
        blank=True,
        default=[]
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

    def get_object_path(self, fs_object, inner_path=None):
        if inner_path is None:
            return os.path.normpath(os.path.join(
                settings.EFSW_STORAGE_ROOT,
                self.base_dir,
                fs_object.path
            ))
        else:
            return os.path.normpath(os.path.join(
                settings.EFSW_STORAGE_ROOT,
                self.base_dir,
                fs_object.path,
                inner_path
            ))

    def get_base_path(self):
        return os.path.normpath(os.path.join(
            settings.EFSW_STORAGE_ROOT,
            self.base_dir
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
        return file_object

    def contains(self, path, check_existence=True):
        if not os.path.exists(self.get_base_path()):
            raise StorageBaseDirNotFound(self.id, self.get_base_path())
        base_dir = self.get_base_path()
        full_path = os.path.normpath(os.path.join(base_dir, path))
        return in_path(base_dir, full_path) and (not check_existence or os.path.exists(full_path))

    INIT_MODE_SKIP_IF_EXISTS = 0
    INIT_MODE_REWRITE_IF_EXISTS = 1

    @classmethod
    def initiate_storage_root(cls, init_mode=None):
        storage_root = os.path.normpath(settings.EFSW_STORAGE_ROOT)
        init_mode = init_mode if init_mode is not None else cls.INIT_MODE_SKIP_IF_EXISTS
        storage_root_mode = settings.EFSW_STORAGE_ROOT_MODE
        if not os.path.exists(storage_root):
            os.makedirs(storage_root, storage_root_mode)
        else:
            if init_mode == cls.INIT_MODE_REWRITE_IF_EXISTS:
                if settings.APP_ENV.lower() != 'prod':
                    # Предварительное переименования появилось из-за того, что в Windows существует задержка между
                    # исполнением команды rmtree и фактическим удалением папки, а переименование происходит сразу
                    tmp_name = '_{0}'.format(storage_root)
                    os.rename(storage_root, tmp_name)
                    shutil.rmtree(tmp_name)
                    os.mkdir(storage_root, storage_root_mode)
                else:
                    raise RuntimeError(storage_errors.STORAGE_ROOT_REWRITE_FORBIDDEN)

    def initiate_storage_base(self, init_mode=None):
        storage_root = os.path.normpath(settings.EFSW_STORAGE_ROOT)
        if not os.path.exists(storage_root):
            raise StorageRootNotFound(storage_root)
        init_mode = init_mode if init_mode is not None else self.INIT_MODE_SKIP_IF_EXISTS
        storage_path = self.get_base_path()
        if not os.path.exists(storage_path):
            os.mkdir(storage_path, settings.EFSW_STORAGE_BASE_DIR_MODE)
        else:
            if init_mode == self.INIT_MODE_REWRITE_IF_EXISTS:
                if settings.APP_ENV.lower() != 'prod':
                    tmp_name = '_{0}'.format(storage_path)
                    os.rename(storage_path, tmp_name)
                    shutil.rmtree(tmp_name)
                    os.mkdir(storage_path, settings.EFSW_STORAGE_BASE_DIR_MODE)
                else:
                    raise RuntimeError(storage_errors.STORAGE_BASE_DIR_REWRITE_FORBIDDEN)


class FileStorageObject(models.Model):

    class Meta:
        app_label = 'storage'
        verbose_name = 'объект в файловом хранилище'
        verbose_name_plural = 'объекты в файловом хранилище'

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

    def get_relative_path(self, inner_path=None):
        if inner_path is None:
            return os.path.normpath(self.path)
        else:
            return os.path.normpath(os.path.join(self.path, inner_path))

    def get_absolute_path(self, inner_path=None):
        return self.storage.get_object_path(self, inner_path)
