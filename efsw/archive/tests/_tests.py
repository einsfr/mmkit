from django.test import TestCase
from django.core import urlresolvers
from django.utils import timezone
from django.core.management import call_command
from django.contrib.auth.models import User, Permission
from django.http import HttpResponse, HttpResponseRedirect

from efsw.archive import models


class ArchiveViewsTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json']

    def test_item_list_category(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item_list_category', args=(2, )))
        self.assertContains(
            response,
            '<h1>Список элементов в категории &laquo;Исходные материалы&raquo;</h1>',
            status_code=200
        )
        self.assertEqual(len(response.context['items']), 3)
        self.assertContains(response, '<a href="#" title="Страница 1">1</a>')

        with self.settings(EFSW_ARCH_ITEM_LIST_PER_PAGE=2):

            response = self.client.get(urlresolvers.reverse('efsw.archive:item_list_category', args=(2, )))
            self.assertContains(
                response,
                '<h1>Список элементов в категории &laquo;Исходные материалы&raquo;</h1>',
                status_code=200
            )
            self.assertEqual(len(response.context['items']), 2)
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')
            self.assertContains(
                response,
                '<a href="/archive/items/category/2/page/2/" title="Следующая страница">»</a>')

            response = self.client.get(urlresolvers.reverse('efsw.archive:item_list_category_page', args=(2, 2, )))
            self.assertContains(
                response,
                '<h1>Список элементов в категории &laquo;Исходные материалы&raquo;</h1>',
                status_code=200
            )
            self.assertEqual(len(response.context['items']), 1)
            self.assertContains(response, '<a href="#" title="Страница 2">2</a>')
            self.assertContains(
                response,
                '<a href="/archive/items/category/2/page/1/" title="Предыдущая страница">«</a>'
            )

    def test_category_list(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:category_list'))
        self.assertContains(response, '<h1>Список категорий</h1>', status_code=200)
        self.assertEqual(len(response.context['object_list']), 3)

    def test_category_add(self):
        request_url = urlresolvers.reverse('efsw.archive:category_add')

        self._login_user()
        response = self.client.get(request_url)
        self.assertContains(response, '<h1>Добавление категории</h1>', status_code=200)
        self.assertContains(response, '<form action="" method="post">')

        with self.assertRaises(models.ItemCategory.DoesNotExist):
            ic = models.ItemCategory.objects.get(name='Новая категория')
        post_data = {
            'name': 'Новая категория'
        }
        response = self.client.post(request_url, post_data, follow=True)
        self.assertContains(response, '<h1>Список категорий</h1>', status_code=200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(len(response.context['object_list']), 4)
        ic = models.ItemCategory.objects.get(name='Новая категория')
        self.assertEqual(ic.name, 'Новая категория')

        response = self.client.post(request_url, post_data)
        self.assertContains(response, '<h1>Добавление категории</h1>', status_code=200)
        self.assertFormError(response, 'form', 'name', 'Категория с таким Название уже существует.')

        post_data = {
            'name': 'a' * 65
        }
        response = self.client.post(request_url, post_data)
        self.assertContains(response, '<h1>Добавление категории</h1>', status_code=200)
        self.assertFormError(
            response,
            'form',
            'name',
            'Убедитесь, что это значение содержит не более 64 символов (сейчас 65).'
        )

    def test_category_update(self):
        request_url = urlresolvers.reverse('efsw.archive:category_update', args=(1, ))

        self._login_user()
        response = self.client.get(request_url)
        self.assertContains(response, '<h1>Редактирование категории</h1>', status_code=200)
        self.assertContains(response, '<form action="" method="post">')

        cat_count = models.ItemCategory.objects.count()
        post_data = {
            'name': 'Отредактированное название'
        }
        response = self.client.post(request_url, post_data, follow=True)
        self.assertContains(response, '<h1>Список категорий</h1>')
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(models.ItemCategory.objects.count(), cat_count)
        self.assertEqual(models.ItemCategory.objects.get(pk=1).name, 'Отредактированное название')


class ArchiveSecurityTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json', 'storage.json', 'itemlog.json', 'itemlocation.json']

    REQUEST_URLS = (
        (urlresolvers.reverse('efsw.archive:search_page', args=(1, )), True),
        (urlresolvers.reverse('efsw.archive:search'), True),
        (urlresolvers.reverse('efsw.archive:item_list'), True),
        (urlresolvers.reverse('efsw.archive:item_list_page', args=(1, )), True),
        (urlresolvers.reverse('efsw.archive:item_list_category', args=(1, )), True),
        (urlresolvers.reverse('efsw.archive:item_list_category_page', args=(1, 1)), True),
        (urlresolvers.reverse('efsw.archive:item_detail', args=(1, )), True),
        (urlresolvers.reverse('efsw.archive:ajax_item_includes_get', args=(1, )), True),
        (urlresolvers.reverse('efsw.archive:ajax_item_locations_get', args=(1, )), True),
        (urlresolvers.reverse('efsw.archive:item_log', args=(1, )), True),
        (
            urlresolvers.reverse('efsw.archive:ajax_item_includes_post', args=(1, )),
            False,
            'change_item',
            None,
            200
        ),
        (
            urlresolvers.reverse('efsw.archive:ajax_item_locations_post', args=(1, )),
            False,
            'change_itemlocation',
            None,
            200
        ),
        (
            urlresolvers.reverse('efsw.archive:item_add'),
            False,
            'add_item',
            '<h1>Добавление элемента</h1>',
            200
        ),
        (
            urlresolvers.reverse('efsw.archive:item_update', args=(1, )),
            False,
            'change_item',
            '<h1>Редактирование элемента</h1>',
            200
        ),
        (urlresolvers.reverse('efsw.archive:category_list'), True),
        (
            urlresolvers.reverse('efsw.archive:category_add'),
            False,
            'add_itemcategory',
            '<h1>Добавление категории</h1>',
            200
        ),
        (
            urlresolvers.reverse('efsw.archive:category_update', args=(1, )),
            False,
            'change_itemcategory',
            '<h1>Редактирование категории</h1>',
            200
        ),
    )

    LOGIN_PATH = 'http://testserver/accounts/login/?next={0}'

    _created_users = []

    # За удаление пользователей, созданных во время тестов, спасибо сюда:
    # https://vilimpoc.org/blog/2013/07/04/django-testing-creating-and-removing-test-users/
    def setUp(self):
        self._users_before = list(User.objects.values_list('id', flat=True).order_by('id'))

    def tearDown(self):
        users_after = list(User.objects.values_list('id', flat=True).order_by('id'))
        users_to_remove = sorted(list(set(users_after) - set(self._users_before)))
        User.objects.filter(id__in=users_to_remove).delete()

    def assertNotLoginRequired(self, response, url_tuple):
        if response.status_code == 302:
            self.assertNotEqual(self.LOGIN_PATH.format(url_tuple[0]), response.redirect_chain[0][0])
            self.assertNotContains(response, '<h1>Вход в систему</h1>')

    def assertLoginRequired(self, response, url_tuple):
        if isinstance(response, HttpResponseRedirect):
            self.assertEqual(self.LOGIN_PATH.format(url_tuple[0]), response.url)
        elif isinstance(response, HttpResponse) and len(response.redirect_chain):
            self.assertEqual(self.LOGIN_PATH.format(url_tuple[0]), response.redirect_chain[0][0])
            self.assertContains(response, '<h1>Вход в систему</h1>')

    def _get_permission_instance(self, codename):
        # Спасибо за идею сюда:
        # https://github.com/lambdalisue/django-permission/blob/master/src/permission/utils/permissions.py
        return Permission.objects.get(
            content_type__app_label='archive',
            codename=codename
            )

    def test_anonymous_access(self):
        self.client.logout()
        for u in self.REQUEST_URLS:
            response = self.client.get(u[0])
            if u[1]:
                self.assertNotLoginRequired(response, u)
            else:
                self.assertLoginRequired(response, u)

    def test_admin_access(self):
        user = User.objects.create_superuser('_sec_admin', 'admin@example.com', '_sec_admin')
        user.save()
        self.client.login(username='_sec_admin', password='_sec_admin')
        for u in self.REQUEST_URLS:
            response = self.client.get(u[0], follow=True)
            self.assertNotLoginRequired(response, u)

    def test_concrete_permissions(self):
        for u in [x for x in self.REQUEST_URLS if not x[1]]:
            codename = u[2]
            username = '_perm_{0}'.format(codename)
            if username not in self._created_users:
                user = User.objects.create_user(username, password='password')
                user.user_permissions.add(self._get_permission_instance(codename))
                user.save()
                self._created_users.append(username)
            self.client.login(username=username, password='password')
            response = self.client.get(u[0])
            if u[3] is not None:
                self.assertContains(response, u[3], status_code=u[4])
            else:
                self.assertEqual(response.status_code, u[4])