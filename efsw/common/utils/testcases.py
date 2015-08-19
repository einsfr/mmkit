import json

from django.test import TestCase
from django.core import urlresolvers
from django.contrib.auth.models import User, Permission
from django.http import HttpResponse, HttpResponseRedirect

from efsw.common.http.response import JsonWithStatusResponse


class UrlsTestCase(TestCase):

    def process_urls(self, url_list):
        for u in url_list:
            (view_name, args, url, view_func) = u
            print('Testing "{0}"... '.format(view_name), end='')
            self.assertEqual(url, urlresolvers.reverse(view_name, args=args))
            resolved_url = urlresolvers.resolve(url)
            self.assertEqual(view_func.__name__, resolved_url.func.__name__)
            self.assertEqual(view_func.__module__, resolved_url.func.__module__)
            print('OK')


class LoginRequiredTestCase(TestCase):

    # За удаление пользователей, созданных во время тестов, спасибо сюда:
    # https://vilimpoc.org/blog/2013/07/04/django-testing-creating-and-removing-test-users/
    def setUp(self):
        self._users_before = list(User.objects.values_list('id', flat=True).order_by('id'))
        user = User.objects.create_superuser('_test', 'test@example.com', '_test')
        user.save()

    def tearDown(self):
        users_after = list(User.objects.values_list('id', flat=True).order_by('id'))
        users_to_remove = sorted(list(set(users_after) - set(self._users_before)))
        User.objects.filter(id__in=users_to_remove).delete()

    def _login_user(self):
        self.client.login(username='_test', password='_test')


class SecurityTestConditions:

    def __init__(self, url, anonymous=True, method='get', perm_codename=None, status_codes=None):
        self.url = url
        self.anonymous = anonymous
        self.method = method
        self.perm_codename = perm_codename
        self.status_codes = status_codes if status_codes is not None else [200, 302]


class AbstractSecurityTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._users_before = []
        self._created_users = []

    def setUp(self):
        self._users_before = list(User.objects.values_list('id', flat=True).order_by('id'))

    def tearDown(self):
        users_after = list(User.objects.values_list('id', flat=True).order_by('id'))
        users_to_remove = sorted(list(set(users_after) - set(self._users_before)))
        User.objects.filter(id__in=users_to_remove).delete()

    def assertNotLoginRequired(self, response, condition):
        if response.status_code == 302:
            self.assertNotEqual(self._get_login_path().format(condition.url), response.redirect_chain[0][0])
            self.assertNotContains(response, '<h2>Вход в систему</h2>')

    def assertLoginRequired(self, response, condition):
        if isinstance(response, HttpResponseRedirect):
            self.assertEqual(self._get_login_path().format(condition.url), response.url)
        elif isinstance(response, HttpResponse) and len(response.redirect_chain):
            self.assertEqual(self._get_login_path().format(condition.url), response.redirect_chain[0][0])
            self.assertContains(response, '<h2>Вход в систему</h2>')

    def _test_anonymous_access(self):
        print('Проверка доступа анонимных пользователей...')
        self.client.logout()
        for c in self._get_test_conditions():
            print('    {0}'.format(c.url), end='')
            if c.method == 'get':
                response = self.client.get(c.url)
            else:
                response = self.client.post(c.url)
            if response.status_code not in c.status_codes:
                raise AssertionError(
                    'При обращении по адресу "{0}" получен код ответа {1}, ожидалось: {2}'.format(
                        c.url,
                        response.status_code,
                        ', '.join(map(str, c.status_codes))
                    )
                )
            if c.anonymous:
                self.assertNotLoginRequired(response, c)
                print(' OK (разрешено)')
            else:
                self.assertLoginRequired(response, c)
                print(' OK (запрещено)')
        print()

    def _test_admin_access(self):
        print('Проверка доступа суперпользователя...')
        User.objects.create_superuser('_sec_admin', 'admin@example.com', 'password')
        self.client.login(username='_sec_admin', password='password')
        for c in self._get_test_conditions():
            print('    {0}'.format(c.url), end='')
            if c.method == 'get':
                response = self.client.get(c.url, follow=True)
            else:
                response = self.client.post(c.url, follow=True)
            if response.status_code not in c.status_codes:
                raise AssertionError(
                    'При обращении по адресу "{0}" получен код ответа {1}, ожидалось: {2}'.format(
                        c.url,
                        response.status_code,
                        ', '.join(map(str, c.status_codes))
                    )
                )
            self.assertNotLoginRequired(response, c)
            print(' OK')
        print()

    def _test_non_priveleged_access(self):
        print('Проверка доступа пользователя без привелегий...')
        User.objects.create_user('_sec_non_priveleged', password='password')
        self.client.login(username='_sec_non_priveleged', password='password')
        for c in self._get_test_conditions():
            print('    {0}'.format(c.url), end='')
            if c.method == 'get':
                response = self.client.get(c.url, follow=True)
            else:
                response = self.client.post(c.url, follow=True)
            if response.status_code not in c.status_codes:
                raise AssertionError(
                    'При обращении по адресу "{0}" получен код ответа {1}, ожидалось: {2}'.format(
                        c.url,
                        response.status_code,
                        ', '.join(map(str, c.status_codes))
                    )
                )
            if c.anonymous:
                self.assertNotLoginRequired(response, c)
                print(' OK (разрешено)')
            else:
                self.assertLoginRequired(response, c)
                print(' OK (запрещено)')
        print()

    def _test_concrete_permissions(self):
        print('Проверка конкретных привелегий...')
        for c in [x for x in self._get_test_conditions() if not x.anonymous]:
            print('    {0}'.format(c.url), end='')
            username = '_perm_{0}'.format(c.perm_codename)
            if username not in self._created_users:
                user = User.objects.create_user(username, password='password')
                user.user_permissions.add(self._get_permission_instance(c.perm_codename))
                user.save()
                self._created_users.append(username)
            self.client.login(username=username, password='password')
            if c.method == 'get':
                response = self.client.get(c.url)
            else:
                response = self.client.post(c.url)
            if response.status_code not in c.status_codes:
                raise AssertionError(
                    'При обращении по адресу "{0}" получен код ответа {1}, ожидалось: {2}'.format(
                        c.url,
                        response.status_code,
                        ', '.join(map(str, c.status_codes))
                    )
                )
            self.assertNotLoginRequired(response, c)
            print(' OK')
        print()

    def _get_permission_instance(self, codename):
        # Спасибо за идею сюда:
        # https://github.com/lambdalisue/django-permission/blob/master/src/permission/utils/permissions.py
        return Permission.objects.get(
            content_type__app_label=self._get_app_label(),
            codename=codename
            )

    def _get_login_path(self):
        raise NotImplementedError()

    def _get_test_conditions(self):
        raise NotImplementedError()

    def _get_app_label(self):
        raise NotImplementedError()


class JsonResponseTestCase(TestCase):

    def assertJsonStatus(self, response, status, status_ext=None, data=None):
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(status, json_content['status'])
        if status_ext is not None:
            self.assertEqual(status_ext, json_content['status_ext'])
        if data is not None:
            self.assertEqual(data, json_content['data'])

    def assertJsonOk(self, response, status_ext=None, data=None):
        self.assertJsonStatus(response, JsonWithStatusResponse.STATUS_OK, status_ext, data)

    def assertJsonError(self, response, status_ext=None, data=None):
        self.assertJsonStatus(response, JsonWithStatusResponse.STATUS_ERROR, status_ext, data)
