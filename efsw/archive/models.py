from django.db import models
from django.core import urlresolvers
from django.contrib.auth.models import User

from efsw.common.search.models import IndexableModel
from efsw.common import models as common_models


class ItemCategory(models.Model):
    """ Модель, описывающая категории элементов """

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        app_label = 'archive'
        ordering = ['name']

    name = models.CharField(
        max_length=64,
        verbose_name='название',
        unique=True
    )

    def __str__(self):
        return self.name


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
        return urlresolvers.reverse('efsw.archive:item:show', args=(self.id, ))

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


class ItemFileLocation(models.Model):

    class Meta:
        app_label = 'archive'
        default_permissions = ()

    file_object = models.OneToOneField(
        common_models.FileStorageObject,
        primary_key=True
    )

    item = models.ForeignKey(
        Item,
        related_name='file_locations'
    )


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
        if type(item) != list:
            item = [item]
        for i in item:
            il = cls()
            il.action = action
            if request.user.is_authenticated():
                user = request.user
            else:
                user = None
            il.user = user
            il.item = i
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
