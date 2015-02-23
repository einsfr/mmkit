from django.test import TestCase

from efsw.common.search.query import EsSearchQuery
from efsw.common.search import elastic


class SearchQueryTestCase(TestCase):

    def test_init(self):
        q = EsSearchQuery(elastic.get_connection_manager())