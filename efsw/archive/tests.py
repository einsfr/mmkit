import os

from django.test import TestCase
from django.core import urlresolvers
from django.utils import timezone

from efsw.archive import models


class ArchiveTestCase(TestCase):
    """ Набор тестов для efsw.archive """

    fixtures = []

    def test_storage_build_path(self):
        storage = models.Storage()
        storage.base_url = "\\\\192.168.1.1"
        self.assertEqual(storage.build_path(1), os.path.join(storage.base_url, '00', '00', '00', '01'))
        self.assertEqual(storage.build_path(476), os.path.join(storage.base_url, '00', '00', '01', 'dc'))
        self.assertEqual(storage.build_path(1000000000), os.path.join(storage.base_url, '3b', '9a', 'ca', '00'))

    def test_object_not_found(self):

        non_exist_object_id = 1000000

        response = self.client.get(urlresolvers.reverse('efsw.archive:item_detail', args=(non_exist_object_id, )))
        self.assertEqual(response.status_code, 404)

    def test_itemlog_get_action_name(self):
        il = models.ItemLog()
        il.dt = timezone.now()
        il.action = il.ACTION_ADD

        self.assertEqual(il.get_action_name(), il.ACTION_DICT[il.ACTION_ADD])

        il.action = 'fake-action'
        self.assertEqual(il.get_action_name(), '')

    def test_item_signals(self):
        s = models.Storage()
        s.name = 'Тестовое хранилище'
        s.base_url = ''
        s.save()

        c = models.ItemCategory()
        c.name = 'Тестовая категория'
        c.save()

        i = models.Item()
        i.name = 'Тестовый элемент'
        i.description = 'Описание тестового элемента'
        i.created = timezone.now()
        i.author = 'Автор тестового элемента'
        i.storage = s
        i.category = c
        i.save()

        # проверка внесения записей в лог
        self.assertEqual(len(i.log.all()), 1)
        self.assertEqual(i.log.all()[0].action, models.ItemLog.ACTION_ADD)
        i.name = 'Изменённый тестовый элемент'
        i.save()
        self.assertEqual(len(i.log.all()), 2)
        self.assertEqual(i.log.all()[1].action, models.ItemLog.ACTION_UPDATE)

        # проверка создания папки по-умолчанию
        self.assertEqual(len(i.folders.all()), 1)
        self.assertEqual(i.folders.all()[0].name, models.ItemFolder.DEFAULT_FOLDER_NAME)