import os

from django.db import models
from django.core import urlresolvers


class Storage(models.Model):
    """ Модель, описывающая архивное онлайн хранилище """

    name = models.CharField(max_length=255)
    base_url = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

    def build_path(self, item_id):
        formatted_id = "{:0>8}".format(hex(item_id)[2:])
        path_list = [formatted_id[x:x+2] for x in range(0, len(formatted_id), 2)]
        return os.path.join(self.base_url, *path_list)


class ItemCategory(models.Model):
    """ Модель, описывающая категории файлов """

    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Item(models.Model):
    """ Модель, описывающая элемент архива """

    name = models.CharField(max_length=255)
    description = models.TextField()
    created = models.DateField()
    author = models.CharField(max_length=255)

    storage = models.ForeignKey(Storage, related_name='items')
    category = models.ForeignKey(ItemCategory, related_name='items')
    includes = models.ManyToManyField('self', symmetrical=False, related_name='included_in')

    def __str__(self):
        return self.name

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


class ItemFolder(models.Model):
    """ Модель, описывающая дочерние папки, принадлежащие элементу архива """

    DEFAULT_FOLDER_NAME = 'default'

    name = models.CharField(max_length=32)

    item = models.ForeignKey(Item, related_name='folders')

    def __str__(self):
        return self.name


class ItemFile(models.Model):
    """ Модель, описывающая файлы, принадлежащие элементу архива """

    name = models.CharField(max_length=255)

    folder = models.ForeignKey(ItemFolder, related_name='files')

    def __str__(self):
        return self.name


class ItemLog(models.Model):
    """ Модель, описывающая журнал элемента """

    ACTION_ADD = 'ADD'
    ACTION_UPDATE = 'UPD'

    ACTION_DICT = {
        ACTION_ADD: 'Добавление',
        ACTION_UPDATE: 'Обновление',
    }

    item = models.ForeignKey(Item, related_name='log')

    dt = models.DateTimeField(auto_now=True)
    action = models.CharField(max_length=3, choices=ACTION_DICT.items())

    def __str__(self):
        return "{0}: {1}".format(self.dt, self.action)

    def get_action_name(self):
        return self.ACTION_DICT.get(str(self.action), '')