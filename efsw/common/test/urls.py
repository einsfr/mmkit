from django.test import TestCase
from django.core import urlresolvers


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