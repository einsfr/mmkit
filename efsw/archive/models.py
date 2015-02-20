import os

from django.db import models
from django.core import urlresolvers
from django.conf import settings

from efsw.archive import default_settings
from efsw.common.search.models import IndexableModel


class Storage(models.Model):
    """ Модель, описывающая архивное онлайн хранилище """

    class Meta:
        verbose_name = 'хранилище'
        verbose_name_plural = 'хранилищи'

    name = models.CharField(
        max_length=255,
        verbose_name='имя'
    )
    # это URL для доступа пользователей
    base_url = models.CharField(
        max_length=255,
        verbose_name='базовая ссылка'
    )
    # а это путь внутри папки EFSW_ARCH_STORAGE_ROOT для операций с файловой системой, его нужно проверять на присутствие только букв и цифр
    mount_dir = models.CharField(
        max_length=32,
        verbose_name='точка монтирования'
    )

    def __str__(self):
        return self.name

    def _build_path_list(self, item_id):
        formatted_id = "{:0>8}".format(hex(item_id)[2:])
        return [formatted_id[x:x+2] for x in range(0, len(formatted_id), 2)]

    def build_url(self, item_id):
        path_list = self._build_path_list(item_id)
        return os.path.join(self.base_url, *path_list)

    def build_path(self, item_id=0):
        if item_id:
            path_list = self._build_path_list(item_id)
        else:
            path_list = []
        storage_root = getattr(settings, 'EFSW_ARCH_STORAGE_ROOT', default_settings.EFSW_ARCH_STORAGE_ROOT)
        return os.path.join(storage_root, self.mount_dir, *path_list)


class ItemCategory(models.Model):
    """ Модель, описывающая категории файлов """

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

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
        return self.storage.build_url(self.id)

    def get_storage_path(self):
        return self.storage.build_path(self.id)

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

    def __str__(self):
        return "{0}: {1}".format(self.dt, self.action)

    def get_action_name(self):
        return self.ACTION_DICT.get(str(self.action), '')