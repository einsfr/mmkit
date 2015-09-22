from efsw.conversion import views
from efsw.common.utils.testcases import UrlsTestCase


class ConversionUrlsTestCase(UrlsTestCase):

    def test_urls(self):
        urls = []
        self.process_urls(urls)
