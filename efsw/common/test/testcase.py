from django.test import TestCase
from django.core import urlresolvers
from django.contrib.auth.models import User


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


class AbstractSecurityTestCase(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._users_before = []

    def setUp(self):
        self._users_before = list(User.objects.values_list('id', flat=True).order_by('id'))

    def tearDown(self):
        users_after = list(User.objects.values_list('id', flat=True).order_by('id'))
        users_to_remove = sorted(list(set(users_after) - set(self._users_before)))
        User.objects.filter(id__in=users_to_remove).delete()

    def assertNotLoginRequired(self, response, url_tuple):
        if response.status_code == 302:
            self.assertNotEqual(self._get_login_path().format(url_tuple[0]), response.redirect_chain[0][0])
            self.assertNotContains(response, '<h1>Вход в систему</h1>')

    def _get_login_path(self):
        raise NotImplementedError()