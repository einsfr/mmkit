import os

from django.db import models
from django.core import urlresolvers
from django.conf import settings
from django.contrib.auth.models import User

from efsw.archive import default_settings
from efsw.common.search.models import IndexableModel
from efsw.common.utils import urlformatter


class ItemCategory(models.Model):
    """ Модель, описывающая категории элементов """

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

    @staticmethod
    def get_update_url_title():
        return 'Редактировать категорию'


class Item(IndexableModel, models.Model):
    """
    Модель, описывающая элемент архива. Для упрощения исходим из того, что каждый элемент в архиве онлайн-типа - это
    папка, в которой есть некоторое количество файлов. Даже если этот файл всего один - всё равно сам элемент будет
    папкой. Зарегистрировать одну папку проще, чем кучу файлов.
    """

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

    def get_absolute_url(self):
        return urlresolvers.reverse('efsw.archive:item_detail', args=(self.id, ))

    @staticmethod
    def get_absolute_url_title():
        return 'Детали элемента'

    def get_update_url(self):
        return urlresolvers.reverse('efsw.archive:item_update', args=(self.id, ))

    @staticmethod
    def get_update_url_title():
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


class Storage(models.Model):
    """ Модель, описывающая архивное хранилище """

    class Meta:
        app_label = 'archive'
        verbose_name = 'хранилище'
        verbose_name_plural = 'хранилищи'

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

    description = models.CharField(
        max_length=255,
        verbose_name='описание'
    )

    base_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='базовая ссылка'
    )

    mount_dir = models.CharField(
        max_length=32,
        blank=True,
        verbose_name='точка монтирования'
    )

    items = models.ManyToManyField(
        Item,
        through='ItemLocation',
        related_name='stored_in'
    )

    def __str__(self):
        return self.name

    def is_online_type(self):
        return self.type == self.TYPE_ONLINE_MASTER or self.type == self.TYPE_ONLINE_SLAVE

    def is_online_master_type(self):
        return self.type == self.TYPE_ONLINE_MASTER

    def is_online_slave_type(self):
        return self.type == self.TYPE_ONLINE_SLAVE

    def is_offline_type(self):
        return self.type == self.TYPE_OFFLINE


class ItemLocation(models.Model):
    """
    Модель, описывающая расположение элементов в хранилищах
    """

    class Meta:
        app_label = 'archive'
        verbose_name = 'размещение моделей в хранилищах'
        unique_together = ('storage', 'item')
        default_permissions = ('change', )

    storage = models.ForeignKey(
        Storage,
        related_name='locations'
    )

    item = models.ForeignKey(
        Item,
        related_name='locations'
    )

    location = models.CharField(
        max_length=255,
        verbose_name='размещение'
    )

    def get_url(self):
        return urlformatter.format_url('{0}/{1}'.format(self.storage.base_url, self.location))

    def get_path(self):
        storage_root = getattr(settings, 'EFSW_ARCH_STORAGE_ROOT', default_settings.EFSW_ARCH_STORAGE_ROOT)
        return os.path.join(storage_root, self.storage.mount_dir, self.location)

    def save(self, *args, **kwargs):
        if self.storage.is_online_master_type():
            self.location = '/'.join(self.build_path_list(self.item.id))
        super().save(*args, **kwargs)

    @staticmethod
    def build_path_list(item_id):
        formatted_id = "{:0>8}".format(hex(item_id)[2:])
        return [formatted_id[x:x+2] for x in range(0, len(formatted_id), 2)]


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