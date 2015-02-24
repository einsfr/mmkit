import os
import json

from django.test import TestCase
from django.test.utils import override_settings
from django.conf import settings
from django.core.management import call_command

from elasticsearch import helpers

from efsw.common.search.query import EsSearchQuery
from efsw.common.search import elastic
from efsw.common.search.exceptions import WrongParametersException


class SearchQueryTestCase(TestCase):

    def test_init(self):
        q = EsSearchQuery(None)
        self.assertIsNone(q._index_name)
        self.assertIsNone(q._doc_type)
        self.assertEqual(q._bool_default, q.BOOL_MUST)
        q = EsSearchQuery(None, 'testindex', 'testtype', EsSearchQuery.BOOL_SHOULD)
        self.assertEqual(q._index_name, 'testindex')
        self.assertEqual(q._doc_type, 'testtype')
        self.assertEqual(q._bool_default, q.BOOL_SHOULD)
        with self.assertRaises(WrongParametersException):
            q = EsSearchQuery(None, bool_default='non-exist-bool-type')

    def test_query_match_all(self):
        q = EsSearchQuery(None)
        q.query_match_all()
        self.assertEqual(q.get_query_body(), {'query': {'match_all': {}}})

    def test_query_multi_match(self):
        q = EsSearchQuery(None)
        q.query_multi_match('query-text', ['field1', 'field2'])
        self.assertEqual(
            q.get_query_body(),
            {
                'query': {
                    'multi_match': {
                        'query': 'query-text',
                        'fields': [
                            'field1',
                            'field2'
                        ]
                    }
                }
            }
        )

    def test_filter_range(self):
        q = EsSearchQuery(None)
        q.filter_terms('field', ['value1', 'value2'])
        self.assertEqual(
            q.get_query_body(),
            {
                'query': {
                    'filtered': {
                        'filter': {
                            'terms': {
                                'field': ['value1', 'value2']
                            }
                        }
                    }
                }
            }
        )

    def test_from_size(self):
        q = EsSearchQuery(None)
        q.query_match_all()
        q.from_size(10, 10)
        self.assertEqual(
            q.get_query_body(),
            {
                'query': {
                    'match_all': {}
                },
                'from': 10,
                'size': 10
            }
        )


class SearchQueryExecTestCase(TestCase):

    INDEX_NAME = 'sqindex'
    DOC_TYPE = 'testmapping'

    @override_settings(EFSW_ELASTIC_DISABLE=False)
    def test_exec(self):
        init_indices = (
            os.path.join(getattr(settings, 'BASE_DIR'), 'efsw', 'common', 'tests', 'sqindex.json'),
        )
        with self.settings(EFSW_ELASTIC_INIT_INDICES=init_indices):
            call_command('esinit', replace=True, verbosity=2)
        es_cm = elastic.get_connection_manager()
        es = es_cm.get_es()
        doc_list_path = os.path.join(getattr(settings, 'BASE_DIR'), 'efsw', 'common', 'tests', 'sqdocs.json')
        with open(doc_list_path) as fp:
            bulk_actions = json.load(fp)
        helpers.bulk(es, bulk_actions, refresh=True)

        q = EsSearchQuery(es_cm, self.INDEX_NAME, self.DOC_TYPE)
        q.query_match_all()
        ids_list = [x['_id'] for x in q.get_result()['hits']['hits']]
        self.assertIn('1', ids_list)
        self.assertIn('2', ids_list)
        self.assertEqual(len(ids_list), 2)

        q = EsSearchQuery(es_cm, self.INDEX_NAME, self.DOC_TYPE)
        q.query_match_all()
        q.filter_terms('field_int', [63])
        ids_list = [x['_id'] for x in q.get_result()['hits']['hits']]
        self.assertIn('1', ids_list)
        self.assertEqual(len(ids_list), 1)

        q = EsSearchQuery(es_cm, self.INDEX_NAME,self.DOC_TYPE)
        q.query_match_all()
        q.filter_terms('field_int', [91])
        q.filter_range('field_date', lte='2015-02-21')
        ids_list = [x['_id'] for x in q.get_result()['hits']['hits']]
        self.assertIn('2', ids_list)
        self.assertEqual(len(ids_list), 1)

        q = EsSearchQuery(es_cm, self.INDEX_NAME, self.DOC_TYPE)
        q.query_multi_match('two', ['field_str', 'field_str_two'])
        ids_list = [x['_id'] for x in q.get_result()['hits']['hits']]
        self.assertIn('2', ids_list)
        self.assertEqual(len(ids_list), 1)