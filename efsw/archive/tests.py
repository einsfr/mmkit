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

        include = models.Item()
        include.name = 'Включённый элемент'
        include.description = 'Описание включённого элемента'
        include.created = timezone.now()
        include.author = 'Автор включённого элемента'
        include.storage = s
        include.category = c
        include.save()

        # проверка внесения записей в лог
        self.assertEqual(len(i.log.all()), 1)
        self.assertEqual(i.log.all()[0].action, models.ItemLog.ACTION_ADD)
        i.name = 'Изменённый тестовый элемент'
        i.save()
        self.assertEqual(len(i.log.all()), 2)
        self.assertEqual(i.log.all()[1].action, models.ItemLog.ACTION_UPDATE)
        i.includes.add(include)
        self.assertEqual(len(i.log.all()), 3)
        self.assertEqual(i.log.all()[2].action, models.ItemLog.ACTION_INCLUDE_UPDATE)
        self.assertEqual(len(include.log.all()), 2)
        self.assertEqual(include.log.all()[1].action, models.ItemLog.ACTION_INCLUDE_UPDATE)

    def test_item_fs_signals(self):
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
                self.assertTrue(os.path.isdir(i.get_storage_path()))
            finally:
                if os.path.isdir(test_storage_root):
                    shutil.rmtree(test_storage_root)


class ArchiveViewsTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json']

    def test_item_list(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Список элементов</h1>')
        self.assertEqual(len(response.context['items']), 7)
        self.assertContains(response, '<a href="#" title="Страница 1">1</a>')

    def test_item_list_page(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item_list_page', args=(1, )))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Список элементов</h1>')
        self.assertEqual(len(response.context['items']), 7)
        self.assertContains(response, '<a href="#" title="Страница 1">1</a>')

        response = self.client.get(urlresolvers.reverse('efsw.archive:item_list_page', args=(2, )))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Список элементов</h1>')
        self.assertEqual(len(response.context['items']), 7)
        self.assertContains(response, '<a href="#" title="Страница 1">1</a>')

        with self.settings(EFSW_ARCH_ITEM_LIST_PER_PAGE=2):

            response = self.client.get(urlresolvers.reverse('efsw.archive:item_list_page', args=(1, )))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<h1>Список элементов</h1>')
            self.assertEqual(len(response.context['items']), 2)
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')
            self.assertContains(response, '<a href="/archive/items/page/2/" title="Следующая страница">»</a>')
            self.assertContains(response, '<a href="/archive/items/page/4/" title="Последняя страница">4</a>')

            response = self.client.get(urlresolvers.reverse('efsw.archive:item_list_page', args=(2, )))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<h1>Список элементов</h1>')
            self.assertEqual(len(response.context['items']), 2)
            self.assertContains(response, '<a href="/archive/items/page/1/" title="Предыдущая страница">«</a>')
            self.assertContains(response, '<a href="#" title="Страница 2">2</a>')
            self.assertContains(response, '<a href="/archive/items/page/3/" title="Следующая страница">»</a>')

    def test_item_list_category(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item_list_category', args=(2, )))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Список элементов в категории &laquo;Исходные материалы&raquo;</h1>')
        self.assertEqual(len(response.context['items']), 3)
        self.assertContains(response, '<a href="#" title="Страница 1">1</a>')

        with self.settings(EFSW_ARCH_ITEM_LIST_PER_PAGE=2):

            response = self.client.get(urlresolvers.reverse('efsw.archive:item_list_category', args=(2, )))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<h1>Список элементов в категории &laquo;Исходные материалы&raquo;</h1>')
            self.assertEqual(len(response.context['items']), 2)
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')
            self.assertContains(
                response,
                '<a href="/archive/items/category/2/page/2/" title="Следующая страница">»</a>')

            response = self.client.get(urlresolvers.reverse('efsw.archive:item_list_category_page', args=(2, 2, )))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<h1>Список элементов в категории &laquo;Исходные материалы&raquo;</h1>')
            self.assertEqual(len(response.context['items']), 1)
            self.assertContains(response, '<a href="#" title="Страница 2">2</a>')
            self.assertContains(
                response,
                '<a href="/archive/items/category/2/page/1/" title="Предыдущая страница">«</a>'
            )

    def test_item_detail(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item_detail', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(urlresolvers.reverse('efsw.archive:item_detail', args=(4, )))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Детали элемента</h1>')
        self.assertEqual(len(response.context['object'].includes.all()), 3)
        self.assertEqual(len(response.context['object'].log.all()), 1)

    def test_item_add(self):
        request_path = urlresolvers.reverse('efsw.archive:item_add')

        response = self.client.get(request_path)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Добавление элемента</h1>')
        self.assertContains(response, '<form action="" method="post">')

        post_data = {
            'name': 'Новый элемент',
            'description': 'Описание нового элемента',
            'created': '2015-02-09',
            'author': 'Автор нового элемента',
            'storage': '1',
            'category': '3',
        }
        response = self.client.post(request_path, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertContains(response, '<h1>Детали элемента</h1>')

        response = self.client.post(request_path)
        self.assertEqual(response.status_code, 200)
        for field in ['name', 'description', 'created', 'author', 'storage', 'category']:
            self.assertFormError(response, 'form', field, 'Обязательное поле.')

        post_data = {
            'name': 'a' * 256,
        }
        response = self.client.post(request_path, post_data)
        self.assertFormError(
            response,
            'form',
            'name',
            'Убедитесь, что это значение содержит не более 255 символов (сейчас 256).'
        )

        post_data = {
            'created': 'this-is-not-a-date',
        }
        response = self.client.post(request_path, post_data)
        self.assertFormError(
            response,
            'form',
            'created',
            'Введите правильную дату.'
        )

        post_data = {
            'author': 'a' * 256,
        }
        response = self.client.post(request_path, post_data)
        self.assertFormError(
            response,
            'form',
            'author',
            'Убедитесь, что это значение содержит не более 255 символов (сейчас 256).'
        )

        post_data = {
            'storage': 'non-existent-storage',
        }
        response = self.client.post(request_path, post_data)
        self.assertFormError(
            response,
            'form',
            'storage',
            'Выберите корректный вариант. Вашего варианта нет среди допустимых значений.'
        )

        post_data = {
            'category': 'non-existent-category',
        }
        response = self.client.post(request_path, post_data)
        self.assertFormError(
            response,
            'form',
            'category',
            'Выберите корректный вариант. Вашего варианта нет среди допустимых значений.'
        )

    def test_item_update(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item_update', args=(4, )))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Редактирование элемента</h1>')
        self.assertContains(response, '<form action="" method="post">')

        response = self.client.get(urlresolvers.reverse('efsw.archive:item_update', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

        post_data = {
            'name': 'Отредактированное название',
            'description': 'Отредактированное описание',
            'created': '2015-02-09',
            'author': 'Автор отредактированного элемента',
            'category': '1',
        }
        response = self.client.post(
            urlresolvers.reverse('efsw.archive:item_update', args=(4, )),
            post_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertContains(response, '<h1>Детали элемента</h1>')

    def test_item_update_storage(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item_update_storage', args=(4, )))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h1>Изменение размещения элемента</h1>')
        self.assertContains(response, '<form action="" method="post">')

        response = self.client.get(urlresolvers.reverse('efsw.archive:item_update_storage', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

        post_data = {
            'storage': '2',
        }
        response = self.client.post(
            urlresolvers.reverse('efsw.archive:item_update_storage', args=(4, )),
            post_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertContains(response, '<h1>Детали элемента</h1>')

    def test_item_update_remove_link(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item_update_remove_link', args=(4, )))
        self.assertEqual(response.status_code, 405)

        response = self.client.post(urlresolvers.reverse('efsw.archive:item_update_remove_link', args=(4, )))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(urlresolvers.reverse('efsw.archive:item_update_remove_link', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

        post_data = {
            'removed_id': '5',
        }
        response = self.client.post(
            urlresolvers.reverse('efsw.archive:item_update_remove_link', args=(4, )),
            post_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '4-5')
        i = models.Item.objects.get(pk=4)
        inc = i.includes.all()
        self.assertEqual(len(inc), 2)
        ids = map(lambda o: o.id, inc)
        self.assertIn(6, ids)
        self.assertIn(7, ids)

        post_data = {
            'removed_id': '1000000'
        }
        response = self.client.post(
            urlresolvers.reverse('efsw.archive:item_update_remove_link', args=(4, )),
            post_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '4-1000000')

    def test_item_update_add_link(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item_update_add_link', args=(4, )))
        self.assertEqual(response.status_code, 405)

        response = self.client.post(urlresolvers.reverse('efsw.archive:item_update_add_link', args=(4, )))
        self.assertEqual(response.status_code, 400)

        response = self.client.post(urlresolvers.reverse('efsw.archive:item_update_add_link', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

        post_data = {
            'linked_id': '5',
        }
        response = self.client.post(
            urlresolvers.reverse('efsw.archive:item_update_add_link', args=(4, )),
            post_data
        )
        self.assertEqual(response.status_code, 200)
        i = models.Item.objects.get(pk=4)
        inc = i.includes.all()
        self.assertEqual(len(inc), 3)
        ids = map(lambda o: o.id, inc)
        self.assertIn(5, ids)
        self.assertIn(6, ids)
        self.assertIn(7, ids)
        response = self.client.post(
            urlresolvers.reverse('efsw.archive:item_update_add_link', args=(4, )),
            post_data
        )
        self.assertEqual(response.status_code, 200)

        post_data = {
            'linked_id': '1000000'
        }
        response = self.client.post(
            urlresolvers.reverse('efsw.archive:item_update_add_link', args=(4, )),
            post_data
        )
        self.assertEqual(response.status_code, 400)