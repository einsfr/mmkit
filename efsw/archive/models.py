import os

from django.db import models
from django.core import urlresolvers
from django.conf import settings
from django.contrib.auth.models import User

from efsw.archive import default_settings
from efsw.archive import exceptions
from efsw.common.search.models import IndexableModel
from efsw.common.db.models import AbstractExtraDataModel
from efsw.common.db.extramap import BaseExtraFieldsMapper


class Storage(AbstractExtraDataModel):
    """ Модель, описывающая архивное онлайн хранилище """

    class Meta:
        app_label = 'archive'

    TYPE_OFFLINE = 'OFF'
    TYPE_ONLINE_MASTER = 'ONM'
    TYPE_ONLINE_SLAVE = 'ONS'

    TYPE_DICT = {
        TYPE_OFFLINE: 'Оффлайн',
        TYPE_ONLINE_MASTER: 'Онлайн (с управлением ФС)',
        TYPE_ONLINE_SLAVE: 'Онлайн (без управления ФС)',
    }

    name = models.CharField(
        max_length=255,
        verbose_name='имя'
    )

    type = models.CharField(
        max_length=3,
        choices=TYPE_DICT.items(),
        verbose_name='тип'
    )

    def __str__(self):
        return self.name

    @classmethod
    def set_extra_fields_mapper(cls):
        raise NotImplementedError()

    @classmethod
    def from_db(cls, db, field_names, values):
        if issubclass(cls, Storage):
            super().from_db(db, field_names, values)
        else:
            storage_type = values[field_names.index('type')]
            if storage_type == cls.TYPE_ONLINE_MASTER:
                OnlineMasterStorage.from_db(db, field_names, values)
            elif storage_type == cls.TYPE_ONLINE_SLAVE:
                OnlineSlaveStorage.from_db(db, field_names, values)
            elif storage_type == cls.TYPE_OFFLINE:
                OfflineStorage.from_db(db, field_names, values)
            else:
                raise exceptions.UnknownStorageType('Неизвестный тип хранилища: {0}'.format(storage_type))


class BaseOnlineStorage(Storage):

    class Meta:
        proxy = True
        verbose_name = 'хранилище'
        verbose_name_plural = 'хранилищи'
        app_label = 'archive'

    @classmethod
    def set_extra_fields_mapper(cls):
        mapper = BaseExtraFieldsMapper()
        mapper.add(
            'base_url',
            models.CharField(
                max_length=255,
                verbose_name='базовая ссылка'
            )
        ).add(
            'mount_dir',
            models.CharField(
                max_length=32,
                verbose_name='точка монтирования'
            )
        )
        cls.extra_fields_mapper = mapper

    def build_url(self, item_id, **kwargs):
        raise NotImplementedError()

    def build_path(self, item_id, **kwargs):
        raise NotImplementedError()


class OnlineMasterStorage(BaseOnlineStorage):

    class Meta:
        proxy = True
        verbose_name = 'хранилище'
        verbose_name_plural = 'хранилищи'
        app_label = 'archive'

    def _build_path_list(self, item_id):
        formatted_id = "{:0>8}".format(hex(item_id)[2:])
        return [formatted_id[x:x+2] for x in range(0, len(formatted_id), 2)]

    def build_url(self, item_id, **kwargs):
        path_list = self._build_path_list(item_id)
        return os.path.join(self.extra_data['base_url'], *path_list)

    def build_path(self, item_id=0, **kwargs):
        storage_root = getattr(settings, 'EFSW_ARCH_STORAGE_ROOT', default_settings.EFSW_ARCH_STORAGE_ROOT)
        if item_id:
            path_list = self._build_path_list(item_id)
        else:
            path_list = []
        return os.path.join(storage_root, self.extra_data['mount_dir'], *path_list)


class OnlineSlaveStorage(BaseOnlineStorage):

    class Meta:
        proxy = True
        verbose_name = 'хранилище'
        verbose_name_plural = 'хранилищи'
        app_label = 'archive'

    def build_url(self, item_id, item_path='', **kwargs):
        return os.path.join(self.extra_data['base_url'], item_path)

    def build_path(self, item_id=0, item_path='', **kwargs):
        storage_root = getattr(settings, 'EFSW_ARCH_STORAGE_ROOT', default_settings.EFSW_ARCH_STORAGE_ROOT)
        return os.path.join(storage_root, self.extra_data['mount_dir'], item_path)


class OfflineStorage():

    class Meta:
        proxy = True
        verbose_name = 'хранилище'
        verbose_name_plural = 'хранилищи'
        app_label = 'archive'


class ItemCategory(models.Model):
    """ Модель, описывающая категории файлов """

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        app_label = 'archive'

    name = models.CharField(
        max_length=64,
        verbose_name='название',
        unique=True
    )

    def __str__(self):
        return self.name

    def get_update_url(self):
        return urlresolvers.reverse('efsw.archive:category_update', args=(self.id, ))

    def get_update_url_title(self):
        return 'Редактировать категорию'


class Item(IndexableModel, models.Model):
    """ Модель, описывающая элемент архива """

    class Meta:
        verbose_name = 'элемент'
        verbose_name_plural = 'элементы'
        app_label = 'archive'

    name = models.CharField(
        max_length=255,
        verbose_name='название'
    )
    description = models.TextField(
        verbose_name='описание'
    )
    created = models.DateField(
        verbose_name='дата создания'
    )
    author = models.CharField(
        max_length=255,
        verbose_name='автор'
    )

    storage = models.ForeignKey(
        Storage,
        related_name='items',
        verbose_name='хранилище'
    )
    category = models.ForeignKey(
        ItemCategory,
        related_name='items',
        verbose_name='категория'
    )
    includes = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='included_in'
    )

    def __str__(self):
        return self.name

    def get_storage_url(self):
        try:
            return self.storage.build_url(self.id)
        except exceptions.StorageTypeMismatch:
            return None

    def get_storage_path(self):
        try:
            return self.storage.build_path(self.id)
        except exceptions.StorageTypeMismatch:
            return None

    def get_storage_type(self):
        return self.storage.type

    def get_absolute_url(self):
        return urlresolvers.reverse('efsw.archive:item_detail', args=(self.id, ))

    def get_absolute_url_title(self):
        return 'Детали элемента'

    def get_update_url(self):
        return urlresolvers.reverse('efsw.archive:item_update', args=(self.id, ))

    def get_update_url_title(self):
        return 'Редактировать элемент'

    @staticmethod
    def get_index_name():
        return 'efswarchitem'

    @staticmethod
    def get_doc_type():
        return 'item'

    def get_doc_body(self):
        return {
            'name': self.name,
            'description': self.description,
            'created': self.created.isoformat(),
            'author': self.author,
            'category': self.category.id,
        }


class ItemLog(models.Model):
    """ Модель, описывающая журнал элемента """

    class Meta:
        verbose_name = 'запись'
        verbose_name_plural = 'записи'
        default_permissions = ()
        app_label = 'archive'

    ACTION_ADD = 'ADD'
    ACTION_UPDATE = 'UPD'
    ACTION_INCLUDE_UPDATE = 'IUP'

    ACTION_DICT = {
        ACTION_ADD: 'Добавление',
        ACTION_UPDATE: 'Обновление',
        ACTION_INCLUDE_UPDATE: 'Обновление связей',
    }

    item = models.ForeignKey(Item, related_name='log')

    dt = models.DateTimeField(auto_now=True)

    action = models.CharField(max_length=3, choices=ACTION_DICT.items())

    user = models.ForeignKey(User, null=True)

    def __str__(self):
        if self.user:
            username = self.user.username
        else:
            username = '-'
        return "{0} ({1}): {2}".format(self.dt, username, self.action)

    def get_action_name(self):
        return self.ACTION_DICT.get(str(self.action), '')

    @classmethod
    def _log_item_action(cls, item, action, request):
        il = cls()
        il.action = action
        if request.user.is_authenticated():
            user = request.user
        else:
            user = None
        il.user = user
        il.item = item
        il.save()

    @classmethod
    def log_item_add(cls, item, request):
        cls._log_item_action(item, cls.ACTION_ADD, request)

    @classmethod
    def log_item_update(cls, item, request):
        cls._log_item_action(item, cls.ACTION_UPDATE, request)

    @classmethod
    def log_item_include_update(cls, item, request):
        cls._log_item_action(item, cls.ACTION_INCLUDE_UPDATE, request)