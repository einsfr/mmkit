from django.test import TestCase
from django.core import urlresolvers
from django.core.management import call_command


class SearchViewTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:search')

    def setUp(self):
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            call_command('esinit', replace=True, verbosity=2)
            call_command('esindex', 'archive.Item', verbosity=2)

    def test_disable_option(self):
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            response = self.client.get(self.request_url)
        self.assertContains(response, '<h1>Поиск по архиву</h1>', status_code=200)
        response = self.client.get(self.request_url)
        self.assertContains(response, '<h1>Поиск не работает</h1>', status_code=500)

    def test_search_queries_q(self):
        get_data = {'q': 'новость'}
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            response = self.client.get(self.request_url, get_data)
        self.assertContains(response, '<h2>Результаты поиска</h2>', status_code=200)
        self.assertEqual(len(response.context['items']), 2)
        ids = [x.id for x in response.context['items']]
        self.assertIn(4, ids)
        self.assertIn(8, ids)

    def test_search_queries_qo(self):
        get_data = {'q': 'новость', 'o': '1'}
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            response = self.client.get(self.request_url, get_data)
        self.assertContains(response, '<h2>Результаты поиска</h2>', status_code=200)
        items = response.context['items']
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].id, 4)
        self.assertEqual(items[1].id, 8)

    def test_search_queries_qc(self):
        get_data = {'q': 'новость', 'c': 1}
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            response = self.client.get(self.request_url, get_data)
        self.assertContains(response, '<h2>Результаты поиска</h2>', status_code=200)
        items = response.context['items']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, 4)