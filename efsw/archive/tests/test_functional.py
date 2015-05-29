from selenium import webdriver

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import urlresolvers


class SearchTestCase(StaticLiveServerTestCase):

    fixtures = ['item.json', 'itemcategory.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = webdriver.Firefox()
        cls.browser.implicitly_wait(3)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def test_search_enabled(self):
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            self.browser.get('{0}{1}'.format(
                self.live_server_url,
                urlresolvers.reverse('efsw.archive:search')
            ))
        self.assertIn('Поиск по архиву', self.browser.title)

    def test_search_disabled(self):
        self.browser.get('{0}{1}'.format(
            self.live_server_url,
            urlresolvers.reverse('efsw.archive:search')
        ))
        self.assertIn('Поиск не работает', self.browser.title)
