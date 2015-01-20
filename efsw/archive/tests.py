import os
import shutil

from django.test import TestCase
from django.core import urlresolvers
from django.utils import timezone
from django.conf import settings

from efsw.archive import default_settings
from efsw.archive import models


class ArchiveTestCase(TestCase):
    """ Набор тестов для efsw.archive """

    fixtures = []

    def test_storage_build_path(self):
        storage = models.Storage()
        storage.base_url = "\\\\192.168.1.1"
        self.assertEqual(storage.build_url(1), os.path.join(storage.base_url, '00', '00', '00', '01'))
        self.assertEqual(storage.build_url(476), os.path.join(storage.base_url, '00', '00', '01', 'dc'))
        self.assertEqual(storage.build_url(1000000000), os.path.join(storage.base_url, '3b', '9a', 'ca', '00'))

        storage.mount_dir = "test"
        storage_root = getattr(settings, 'EFSW_ARCH_STORAGE_ROOT', default_settings.EFSW_ARCH_STORAGE_ROOT)
        self.assertEqual(storage.build_path(), os.path.join(storage_root, storage.mount_dir))
        self.assertEqual(storage.build_path(1), os.path.join(storage_root, storage.mount_dir, '00', '00', '00', '01'))
        self.assertEqual(storage.build_path(476), os.path.join(storage_root, storage.mount_dir, '00', '00', '01', 'dc'))
        self.assertEqual(storage.build_path(1000000000), os.path.join(storage_root, storage.mount_dir, '3b', '9a', 'ca', '00'))

        item1 = models.Item()
        item1.id = 1
        item1.storage = storage
        self.assertEqual(
            item1.get_storage_path(),
            os.path.join(storage_root, storage.mount_dir, '00', '00', '00', '01')
        )
        item476 = models.Item()
        item476.id = 476
        item476.storage = storage
        self.assertEqual(
            item476.get_storage_path(),
            os.path.join(storage_root, storage.mount_dir, '00', '00', '01', 'dc')
        )
        item1z9 = models.Item()
        item1z9.id = 1000000000
        item1z9.storage = storage
        self.assertEqual(
            item1z9.get_storage_path(),
            os.path.join(storage_root, storage.mount_dir, '3b', '9a', 'ca', '00')
        )

        folder1 = models.ItemFolder()
        folder1.name = 'item1folder'
        folder1.item = item1
        self.assertEqual(
            folder1.get_storage_path(),
            os.path.join(storage_root, storage.mount_dir, '00', '00', '00', '01', folder1.name)
        )
        folder476 = models.ItemFolder()
        folder476.name = 'item476folder'
        folder476.item = item476
        self.assertEqual(
            folder476.get_storage_path(),
            os.path.join(storage_root, storage.mount_dir, '00', '00', '01', 'dc', folder476.name)
        )
        folder1z9_1 = models.ItemFolder()
        folder1z9_1.name = 'item1z9folder1'
        folder1z9_1.item = item1z9
        folder1z9_2 = models.ItemFolder()
        folder1z9_2.name = 'item1z9folder2'
        folder1z9_2.item = item1z9
        self.assertEqual(
            folder1z9_1.get_storage_path(),
            os.path.join(storage_root, storage.mount_dir, '3b', '9a', 'ca', '00', folder1z9_1.name)
        )
        self.assertEqual(
            folder1z9_2.get_storage_path(),
            os.path.join(storage_root, storage.mount_dir, '3b', '9a', 'ca', '00', folder1z9_2.name)
        )

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

    def test_folder_signals(self):
        test_storage_root = os.path.join(settings.BASE_DIR, getattr(settings, 'EFSW_ARCH_STORAGE_ROOT', '_storage_test'))
        with self.settings(EFSW_ARCH_SKIP_FS_OPS=False):
            s = models.Storage()
            s.name = 'storage1'
            s.mount_dir = 'storage1'
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

            if os.path.isdir(test_storage_root):
                shutil.rmtree(test_storage_root)
            os.mkdir(test_storage_root)
            try:
                i.save()
                self.assertTrue(os.path.isdir(os.path.join(i.get_storage_path(), models.ItemFolder.DEFAULT_FOLDER_NAME)))
            finally:
                if os.path.isdir(test_storage_root):
                    shutil.rmtree(test_storage_root)