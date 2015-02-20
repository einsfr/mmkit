import os
import datetime

from django.test import TestCase
from django.db import models
from django.core import paginator
from django.conf import settings
from django.db import connection

from efsw.common.templatetags import model
from efsw.common.templatetags import pagination
from efsw.common import default_settings
from efsw.common.search import elastic
from efsw.common.management.commands import esinit
from efsw.common.tests import models as test_models


class ModelTagTestCase(TestCase):

    class TestModel(models.Model):

        class Meta:
            verbose_name = 'тестомодель'
            verbose_name_plural = 'тестомодели'

        name = models.CharField(
            max_length=255,
            verbose_name='тестовое имя'
        )

    class TestModelWithoutVerbose(models.Model):

        name = models.CharField(
            max_length=255
        )

    class NotModel():
        pass

    def test_prepare_instance(self):
        instance = self.TestModel()
        not_instance = self.NotModel()
        self.assertEqual(model._prepare_instance(instance), instance)
        self.assertEqual(model._prepare_instance([instance]), instance)
        self.assertIsNone(model._prepare_instance(not_instance))
        self.assertIsNone(model._prepare_instance([not_instance]))
        self.assertIsNone(model._prepare_instance([]))

    def test_verbose_name(self):
        not_instance = self.NotModel()
        self.assertEqual(model.verbose_name(not_instance), '')
        self.assertEqual(model.verbose_name(not_instance, False), '')
        self.assertEqual(model.verbose_name(not_instance, True), '')
        self.assertEqual(model.verbose_name(not_instance, False, False), '')
        self.assertEqual(model.verbose_name(not_instance, False, True), '')
        self.assertEqual(model.verbose_name(not_instance, True, False), '')
        self.assertEqual(model.verbose_name(not_instance, True, True), '')
        instance = self.TestModel()
        self.assertEqual(model.verbose_name(instance), 'Тестомодель')
        self.assertEqual(model.verbose_name(instance, False), 'Тестомодель')
        self.assertEqual(model.verbose_name(instance, True), 'Тестомодели')
        self.assertEqual(model.verbose_name(instance, False, False), 'тестомодель')
        self.assertEqual(model.verbose_name(instance, False, True), 'Тестомодель')
        self.assertEqual(model.verbose_name(instance, True, False), 'тестомодели')
        self.assertEqual(model.verbose_name(instance, True, True), 'Тестомодели')
        instance_wo = self.TestModelWithoutVerbose()
        self.assertEqual(model.verbose_name(instance_wo), 'Test model without verbose')
        self.assertEqual(model.verbose_name(instance_wo, False), 'Test model without verbose')
        self.assertEqual(model.verbose_name(instance_wo, True), 'Test model without verboses')
        self.assertEqual(model.verbose_name(instance_wo, False, False), 'test model without verbose')
        self.assertEqual(model.verbose_name(instance_wo, False, True), 'Test model without verbose')
        self.assertEqual(model.verbose_name(instance_wo, True, False), 'test model without verboses')
        self.assertEqual(model.verbose_name(instance_wo, True, True), 'Test model without verboses')

    def test_field_verbose_name(self):
        not_instance = self.NotModel()
        self.assertEqual(model.field_verbose_name(not_instance, 'name'), '')
        self.assertEqual(model.field_verbose_name(not_instance, 'name', False), '')
        self.assertEqual(model.field_verbose_name(not_instance, 'name', True), '')
        self.assertEqual(model.field_verbose_name(not_instance, 'non-exist'), '')
        self.assertEqual(model.field_verbose_name(not_instance, 'non-exist', False), '')
        self.assertEqual(model.field_verbose_name(not_instance, 'non-exist', True), '')
        instance = self.TestModel()
        self.assertEqual(model.field_verbose_name(instance, 'name'), 'Тестовое имя')
        self.assertEqual(model.field_verbose_name(instance, 'name', False), 'тестовое имя')
        self.assertEqual(model.field_verbose_name(instance, 'name', True), 'Тестовое имя')
        self.assertEqual(model.field_verbose_name(instance, 'non-exist'), '')
        self.assertEqual(model.field_verbose_name(instance, 'non-exist', False), '')
        self.assertEqual(model.field_verbose_name(instance, 'non-exist', True), '')
        instance_wo = self.TestModelWithoutVerbose()
        self.assertEqual(model.field_verbose_name(instance_wo, 'name'), 'Name')
        self.assertEqual(model.field_verbose_name(instance_wo, 'name', False), 'name')
        self.assertEqual(model.field_verbose_name(instance_wo, 'name', True), 'Name')
        self.assertEqual(model.field_verbose_name(instance_wo, 'non-exist'), '')
        self.assertEqual(model.field_verbose_name(instance_wo, 'non-exist', False), '')
        self.assertEqual(model.field_verbose_name(instance_wo, 'non-exist', True), '')


class PaginationTagTestCase(TestCase):

    urls = 'efsw.common.tests.tests_urls'

    _next_page_text = getattr(settings, 'EFSW_COMM_PAGIN_NEXT_TEXT', default_settings.EFSW_COMM_PAGIN_NEXT_TEXT)

    _prev_page_text = getattr(settings, 'EFSW_COMM_PAGIN_PREV_TEXT', default_settings.EFSW_COMM_PAGIN_PREV_TEXT)

    def _test_prev_at(self, prep, pos, num, query_string):
        self.assertEqual(prep[pos]['text'], self._prev_page_text)
        self.assertEqual(prep[pos]['url'], '/page/{0}/{1}'.format(num, query_string))
        self.assertFalse(prep[pos]['active'])

    def _test_next_at(self, prep, pos, num, query_string):
        self.assertEqual(prep[pos]['text'], self._next_page_text)
        self.assertEqual(prep[pos]['url'], '/page/{0}/{1}'.format(num, query_string))
        self.assertFalse(prep[pos]['active'])

    def _test_active_num_at(self, prep, pos, num):
        self.assertEqual(prep[pos]['text'], str(num))
        self.assertEqual(prep[pos]['url'], '#')
        self.assertTrue(prep[pos]['active'])

    def _test_num_at(self, prep, pos_num_dict, query_string):
        for pos, num in pos_num_dict.items():
            self.assertEqual(prep[pos]['text'], str(num))
            self.assertEqual(prep[pos]['url'], '/page/{0}/{1}'.format(num, query_string))
            self.assertFalse(prep[pos]['active'])

    def _process_test_list(self, page_count, test_list, query_string=''):
        pagin = paginator.Paginator([x for x in range(1, page_count + 1)], 1)
        page_num = 1
        for test_string in test_list:
            page = pagin.page(page_num)
            prep = pagination._prepare(page, 'page', query_string)
            if query_string:
                query_string = '?{0}'.format(query_string)
            parts = test_string.split(' ')
            self.assertEqual(len(prep), len(parts))
            for num, p in enumerate(parts):
                if p[0] == '<' and p[-1] == '>':
                    self._test_active_num_at(prep, num, int(p[1:-1]))
                    active_page_number = int(p[1:-1])
            pos_num = {}
            for num, p in enumerate(parts):
                if p == self._prev_page_text:
                    self._test_prev_at(prep, num, active_page_number - 1, query_string)
                elif p == self._next_page_text:
                    self._test_next_at(prep, num, active_page_number + 1, query_string)
                elif p[0] != '<' and p[-1] != '>':
                    pos_num[num] = int(p)
            self._test_num_at(prep, pos_num, query_string)
            page_num += 1

    def test_pagination(self):
        """ Тесты для листалки """

        """
        ------ Всего страниц: 1, показывать соседей: 1 ------
        1: <1>
        """

        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            self._process_test_list(1, ['<1>'])

        """
        --- Всего страниц: 1, показывать соседей: 2 ---
        1: <1>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            self._process_test_list(1, ['<1>'])

        """
        --- Всего страниц: 1, показывать соседей: 20 ---
        1: <1>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            self._process_test_list(1, ['<1>'])

        """
        ------ Всего страниц: 2, показывать соседей: 1 ------
        1: <1> 2 >>
        2: << 1 <2>
        """

        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            self._process_test_list(2, ['<1> 2 >>', '<< 1 <2>'])

        """
        --- Всего страниц: 2, показывать соседей: 2 ---
        1: <1> 2 >>
        2: << 1 <2>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            self._process_test_list(2, ['<1> 2 >>', '<< 1 <2>'])

        """
        --- Всего страниц: 2, показывать соседей: 20 ---
        1: <1> 2 >>
        2: << 1 <2>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            self._process_test_list(2, ['<1> 2 >>', '<< 1 <2>'])

        """
        ------ Всего страниц: 3, показывать соседей: 1 ------
        1: <1> 2 >> 3
        2: << 1 <2> 3 >>
        3: 1 << 2 <3>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            self._process_test_list(3, ['<1> 2 >> 3', '<< 1 <2> 3 >>', '1 << 2 <3>'])

        """
        --- Всего страниц: 3, показывать соседей: 2 ---
        1: <1> 2 3 >>
        2: << 1 <2> 3 >>
        3: << 1 2 <3>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            self._process_test_list(3, ['<1> 2 3 >>', '<< 1 <2> 3 >>', '<< 1 2 <3>'])

        """
        --- Всего страниц: 3, показывать соседей: 20 ---
        1: <1> 2 3 >>
        2: << 1 <2> 3 >>
        3: << 1 2 <3>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            self._process_test_list(3, ['<1> 2 3 >>', '<< 1 <2> 3 >>', '<< 1 2 <3>'])

        """
        ------ Всего страниц: 4, показывать соседей: 1 ------
        1: <1> 2 >> 4
        2: << 1 <2> 3 >> 4
        3: 1 << 2 <3> 4 >>
        4: 1 << 3 <4>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            self._process_test_list(4, ['<1> 2 >> 4', '<< 1 <2> 3 >> 4', '1 << 2 <3> 4 >>', '1 << 3 <4>'])

        """
        --- Всего страниц: 4, показывать соседей: 2 ---
        1: <1> 2 3 >> 4
        2: << 1 <2> 3 4 >>
        3: << 1 2 <3> 4 >>
        4: 1 << 2 3 <4>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            self._process_test_list(4, ['<1> 2 3 >> 4', '<< 1 <2> 3 4 >>', '<< 1 2 <3> 4 >>', '1 << 2 3 <4>'])

        """
        --- Всего страниц: 4, показывать соседей: 20 ---
        1: <1> 2 3 4 >>
        2: << 1 <2> 3 4 >>
        3: << 1 2 <3> 4 >>
        4: << 1 2 3 <4>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            self._process_test_list(4, ['<1> 2 3 4 >>', '<< 1 <2> 3 4 >>', '<< 1 2 <3> 4 >>', '<< 1 2 3 <4>'])

        """
        ------ Всего страниц: 5, показывать соседей: 1 ------
        1: <1> 2 >> 5
        2: << 1 <2> 3 >> 5
        3: 1 << 2 <3> 4 >> 5
        4: 1 << 3 <4> 5 >>
        5: 1 << 4 <5>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            self._process_test_list(5, ['<1> 2 >> 5', '<< 1 <2> 3 >> 5', '1 << 2 <3> 4 >> 5', '1 << 3 <4> 5 >>',
                                    '1 << 4 <5>'])

        """
        --- Всего страниц: 5, показывать соседей: 2 ---
        1: <1> 2 3 >> 5
        2: << 1 <2> 3 4 >> 5
        3: << 1 2 <3> 4 5 >>
        4: 1 << 2 3 <4> 5 >>
        5: 1 << 3 4 <5>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            self._process_test_list(5, ['<1> 2 3 >> 5', '<< 1 <2> 3 4 >> 5', '<< 1 2 <3> 4 5 >>', '1 << 2 3 <4> 5 >>',
                                    '1 << 3 4 <5>'])

        """
        --- Всего страниц: 5, показывать соседей: 20 ---
        1: <1> 2 3 4 5 >>
        2: << 1 <2> 3 4 5 >>
        3: << 1 2 <3> 4 5 >>
        4: << 1 2 3 <4> 5 >>
        5: << 1 2 3 4 <5>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            self._process_test_list(5, ['<1> 2 3 4 5 >>', '<< 1 <2> 3 4 5 >>', '<< 1 2 <3> 4 5 >>', '<< 1 2 3 <4> 5 >>',
                                    '<< 1 2 3 4 <5>'])

        """
        ------ Всего страниц: 10, показывать соседей: 1 ------
        1:  <1> 2 >> 10
        2:  << 1 <2> 3 >> 10
        3:  1 << 2 <3> 4 >> 10
        4:  1 << 3 <4> 5 >> 10
        5:  1 << 4 <5> 6 >> 10
        6:  1 << 5 <6> 7 >> 10
        7:  1 << 6 <7> 8 >> 10
        8:  1 << 7 <8> 9 >> 10
        9:  1 << 8 <9> 10 >>
        10: 1 << 9 <10>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            self._process_test_list(10, ['<1> 2 >> 10', '<< 1 <2> 3 >> 10', '1 << 2 <3> 4 >> 10', '1 << 3 <4> 5 >> 10',
                                         '1 << 4 <5> 6 >> 10', '1 << 5 <6> 7 >> 10', '1 << 6 <7> 8 >> 10',
                                         '1 << 7 <8> 9 >> 10', '1 << 8 <9> 10 >>', '1 << 9 <10>'])

        """
        --- Всего страниц: 10, показывать соседей: 2 ---
        1:  <1> 2 3 >> 10
        2:  << 1 <2> 3 4 >> 10
        3:  << 1 2 <3> 4 5 >> 10
        4:  1 << 2 3 <4> 5 6 >> 10
        5:  1 << 3 4 <5> 6 7 >> 10
        6:  1 << 4 5 <6> 7 8 >> 10
        7:  1 << 5 6 <7> 8 9 >> 10
        8:  1 << 6 7 <8> 9 10 >>
        9:  1 << 7 8 <9> 10 >>
        10: 1 << 8 9 <10>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            self._process_test_list(10, ['<1> 2 3 >> 10', '<< 1 <2> 3 4 >> 10', '<< 1 2 <3> 4 5 >> 10',
                                         '1 << 2 3 <4> 5 6 >> 10', '1 << 3 4 <5> 6 7 >> 10', '1 << 4 5 <6> 7 8 >> 10',
                                         '1 << 5 6 <7> 8 9 >> 10', '1 << 6 7 <8> 9 10 >>', '1 << 7 8 <9> 10 >>',
                                         '1 << 8 9 <10>'])

        """
        --- Всего страниц: 10, показывать соседей: 20 ---
        1:  <1> 2 3 4 5 6 7 8 9 10 >>
        2:  << 1 <2> 3 4 5 6 7 8 9 10 >>
        3:  << 1 2 <3> 4 5 6 7 8 9 10 >>
        4:  << 1 2 3 <4> 5 6 7 8 9 10 >>
        5:  << 1 2 3 4 <5> 6 7 8 9 10 >>
        6:  << 1 2 3 4 5 <6> 7 8 9 10 >>
        7:  << 1 2 3 4 5 6 <7> 8 9 10 >>
        8:  << 1 2 3 4 5 6 7 <8> 9 10 >>
        9:  << 1 2 3 4 5 6 7 8 <9> 10 >>
        10: << 1 2 3 4 5 6 7 8 9 <10>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            self._process_test_list(10, ['<1> 2 3 4 5 6 7 8 9 10 >>', '<< 1 <2> 3 4 5 6 7 8 9 10 >>',
                                         '<< 1 2 <3> 4 5 6 7 8 9 10 >>', '<< 1 2 3 <4> 5 6 7 8 9 10 >>',
                                         '<< 1 2 3 4 <5> 6 7 8 9 10 >>', '<< 1 2 3 4 5 <6> 7 8 9 10 >>',
                                         '<< 1 2 3 4 5 6 <7> 8 9 10 >>', '<< 1 2 3 4 5 6 7 <8> 9 10 >>',
                                         '<< 1 2 3 4 5 6 7 8 <9> 10 >>', '<< 1 2 3 4 5 6 7 8 9 <10>'])
            # И ещё раз - с query_string
            self._process_test_list(10, ['<1> 2 3 4 5 6 7 8 9 10 >>', '<< 1 <2> 3 4 5 6 7 8 9 10 >>',
                                         '<< 1 2 <3> 4 5 6 7 8 9 10 >>', '<< 1 2 3 <4> 5 6 7 8 9 10 >>',
                                         '<< 1 2 3 4 <5> 6 7 8 9 10 >>', '<< 1 2 3 4 5 <6> 7 8 9 10 >>',
                                         '<< 1 2 3 4 5 6 <7> 8 9 10 >>', '<< 1 2 3 4 5 6 7 <8> 9 10 >>',
                                         '<< 1 2 3 4 5 6 7 8 <9> 10 >>', '<< 1 2 3 4 5 6 7 8 9 <10>'], 'param=2')


class SearchTestCase(TestCase):

    def testConnection(self):
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            es = elastic.get_connection_manager().get_es()
            another_es = elastic.get_connection_manager().get_es()
        self.assertTrue(es is another_es)

    def testInitialization(self):
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            es = elastic.get_connection_manager().get_es()
        cmd = esinit.Command()
        base_dir = getattr(settings, 'BASE_DIR')
        init_indices = (
            os.path.join(base_dir, 'non-existent-file.json'),
        )
        with self.settings(
                EFSW_ELASTIC_INIT_INDICES=init_indices,
                EFSW_ELASTIC_DISABLE=False
        ):
            with self.assertRaises(FileNotFoundError):
                cmd.handle(replace=True, verbosity=2, nowait=False)

        init_indices = (
            os.path.join(base_dir, 'efsw', 'common', 'tests', 'testindex.json'),
            os.path.join(base_dir, 'efsw', 'common', 'tests', 'indices'),
        )
        with self.settings(
                EFSW_ELASTIC_INIT_INDICES=init_indices,
                EFSW_ELASTIC_DISABLE=False
        ):
            cmd.handle(replace=True, verbosity=2, nowait=False)
        index_prefix = elastic.get_connection_manager().get_es_index_prefix()
        reply = es.indices.get(index='{0}testindex'.format(index_prefix), feature='_mappings')
        self.assertEqual(reply, {
            '{0}testindex'.format(index_prefix): {
                'mappings': {'testmapping': {'properties': {'testproperty': {'type': 'string'}}}}
            }
        })

        reply = es.indices.get(index='{0}andanotherone'.format(index_prefix), feature='_mappings')
        self.assertEqual(reply, {
            '{0}andanotherone'.format(index_prefix): {
                'mappings': {'andanothermapping': {'properties': {'testproperty': {'type': 'string'}}}}
            }
        })

        reply = es.indices.get(index='{0}anotherindex'.format(index_prefix), feature='_mappings')
        self.assertEqual(reply, {
            '{0}anotherindex'.format(index_prefix): {
                'mappings': {'anothermapping': {'properties': {'testproperty': {'type': 'string'}}}}
            }
        })


class ModelIndexTestCase(TestCase):

    def testModelCreation(self):
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            es = elastic.get_connection_manager().get_es()
        init_indices = (
            os.path.join(getattr(settings, 'BASE_DIR'), 'efsw', 'common', 'tests', 'testmodelindex.json'),
        )
        with self.settings(
                EFSW_ELASTIC_INIT_INDICES=init_indices,
                EFSW_ELASTIC_DISABLE=False
        ):
            esinit.Command().handle(replace=True, verbosity=2, nowait=False)
        m = test_models.IndexableTestModel()
        m.name = 'Test Model 1'
        m.created = datetime.date.today()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(m)
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            m.save()
        index_prefix = elastic.get_connection_manager().get_es_index_prefix()
        reply = es.get('{0}testmodelindex'.format(index_prefix), m.id, 'indexabletestmodel')
        self.assertEqual(reply['_index'], '{0}testmodelindex'.format(index_prefix))
        self.assertEqual(reply['_source']['created'], m.created.isoformat())
        self.assertEqual(reply['_source']['name'], m.name)
        self.assertEqual(reply['_type'], 'indexabletestmodel')
        self.assertEqual(reply['_id'], str(m.id))
        self.assertTrue(reply['found'])
        m.name = 'Edited Test Model 1'
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            m.save()
        reply = es.get('{0}testmodelindex'.format(index_prefix), m.id, 'indexabletestmodel')
        self.assertEqual(reply['_index'], '{0}testmodelindex'.format(index_prefix))
        self.assertEqual(reply['_source']['created'], m.created.isoformat())
        self.assertEqual(reply['_source']['name'], m.name)
        self.assertEqual(reply['_type'], 'indexabletestmodel')
        self.assertEqual(reply['_id'], str(m.id))
        self.assertTrue(reply['found'])
        model_id = m.id
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            m.delete()
        reply = es.get('{0}testmodelindex'.format(index_prefix), model_id, 'indexabletestmodel', ignore=404)
        self.assertFalse(reply['found'])
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(m)