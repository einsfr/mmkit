from django.test import TestCase
from django.db import models
from django.core import paginator
from django.conf import settings

from efsw.common.templatetags import model
from efsw.common.templatetags import pagination
from efsw.common import default_settings


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

    urls = 'efsw.common.tests_urls'

    _next_page_text = getattr(settings, 'EFSW_COMM_PAGIN_NEXT_TEXT', default_settings.EFSW_COMM_PAGIN_NEXT_TEXT)

    _prev_page_text = getattr(settings, 'EFSW_COMM_PAGIN_PREV_TEXT', default_settings.EFSW_COMM_PAGIN_PREV_TEXT)

    def _test_prev_at(self, prep, pos, num):
        self.assertEqual(prep[pos]['text'], self._prev_page_text)
        self.assertEqual(prep[pos]['url'], '/page/{0}/'.format(num))
        self.assertFalse(prep[pos]['active'])

    def _test_next_at(self, prep, pos, num):
        self.assertEqual(prep[pos]['text'], self._next_page_text)
        self.assertEqual(prep[pos]['url'], '/page/{0}/'.format(num))
        self.assertFalse(prep[pos]['active'])

    def _test_active_num_at(self, prep, pos, num):
        self.assertEqual(prep[pos]['text'], str(num))
        self.assertEqual(prep[pos]['url'], '#')
        self.assertTrue(prep[pos]['active'])

    def _test_num_at(self, prep, pos_num_dict):
        for pos, num in pos_num_dict.items():
            self.assertEqual(prep[pos]['text'], str(num))
            self.assertEqual(prep[pos]['url'], '/page/{0}/'.format(num))
            self.assertFalse(prep[pos]['active'])

    def _process_test_list(self, page_count, test_list):
        pagin = paginator.Paginator([x for x in range(1, page_count + 1)], 1)
        page_num = 1
        for test_string in test_list:
            page = pagin.page(page_num)
            prep = pagination._prepare(page, 'page')
            parts = test_string.split(' ')
            self.assertEqual(len(prep), len(parts))
            for num, p in enumerate(parts):
                if p[0] == '<' and p[-1] == '>':
                    self._test_active_num_at(prep, num, int(p[1:-1]))
                    active_page_number = int(p[1:-1])
            pos_num = {}
            for num, p in enumerate(parts):
                if p == self._prev_page_text:
                    self._test_prev_at(prep, num, active_page_number - 1)
                elif p == self._next_page_text:
                    self._test_next_at(prep, num, active_page_number + 1)
                elif p[0] != '<' and p[-1] != '>':
                    pos_num[num] = p[1:-1]
            self._test_num_at(prep, pos_num)
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
        tl = [1, 2, ]
        pagin = paginator.Paginator(tl, 1)

        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            self._process_test_list(2, ['<1> 2 >>', '<< 1 <2>'])

            page = pagin.page(2)
            prep = pagination._prepare(page, 'page')
            self.assertEqual(len(prep), 3)
            self._test_active_num_at(prep, 2, 2)
            self._test_num_at(prep, {1: 1})
            self._test_prev_at(prep, 0, 1)

            del page, prep

        """
        --- Всего страниц: 2, показывать соседей: 2 ---
        1: <1> 2 >>
        2: << 1 <2>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            page = pagin.page(1)
            prep = pagination._prepare(page, 'page')
            self.assertEqual(len(prep), 3)
            self._test_active_num_at(prep, 0, 1)
            self._test_num_at(prep, {1: 2})
            self._test_next_at(prep, 2, 2)

            del page, prep

            page = pagin.page(2)
            prep = pagination._prepare(page, 'page')
            self.assertEqual(len(prep), 3)
            self._test_active_num_at(prep, 2, 2)
            self._test_num_at(prep, {1: 1})
            self._test_prev_at(prep, 0, 1)

            del page, prep

        """
        --- Всего страниц: 2, показывать соседей: 20 ---
        1: <1> 2 >>
        2: << 1 <2>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            page = pagin.page(1)
            prep = pagination._prepare(page, 'page')
            self.assertEqual(len(prep), 3)
            self._test_active_num_at(prep, 0, 1)
            self._test_num_at(prep, {1: 2})
            self._test_next_at(prep, 2, 2)

            del page, prep

            page = pagin.page(2)
            prep = pagination._prepare(page, 'page')
            self.assertEqual(len(prep), 3)
            self._test_active_num_at(prep, 2, 2)
            self._test_num_at(prep, {1: 1})
            self._test_prev_at(prep, 0, 1)

            del page, prep, pagin, tl

        """
        ------ Всего страниц: 3, показывать соседей: 1 ------
        1: <1> 2 >> 3
        2: << 1 <2> 3 >>
        3: 1 << 2 <3>
        """

        tl = [1, 2, 3, ]
        pagin = paginator.Paginator(tl, 1)

        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            page = pagin.page(1)
            prep = pagination._prepare(page, 'page')
            self.assertEqual(len(prep), 4)
            self._test_active_num_at(prep, 0, 1)
            self._test_num_at(prep, {1: 2, 3: 3})
            self._test_next_at(prep, 2, 2)

            del page, prep

            page = pagin.page(2)
            prep = pagination._prepare(page, 'page')
            self.assertEqual(len(prep), 5)
            self._test_active_num_at(prep, 2, 2)
            self._test_num_at(prep, {1: 1, 3: 3})
            self._test_prev_at(prep, 0, 1)
            self._test_next_at(prep, 4, 3)

            del page, prep

            page = pagin.page(3)
            prep = pagination._prepare(page, 'page')
            self.assertEqual(len(prep), 4)
            self._test_active_num_at(prep, 3, 3)
            self._test_num_at(prep, {0: 1, 2: 2})
            self._test_prev_at(prep, 1, 2)

            del page, prep

        """
        --- Всего страниц: 3, показывать соседей: 2 ---
        1: <1> 2 3 >>
        2: << 1 <2> 3 >>
        3: << 1 2 <3>
        """
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            page = pagin.page(1)
            prep = pagination._prepare(page, 'page')
            self.assertEqual(len(prep), 4)
            self.assertEqual(prep[0]['text'], '1')
            self.assertEqual(prep[0]['url'], '#')
            self.assertTrue(prep[0]['active'])
            for i in range(1, 3):
                self.assertEqual(prep[i]['text'], str(i + 1))
                self.assertEqual(prep[i]['url'], '/page/{0}/'.format(i + 1))
                self.assertFalse(prep[i]['active'])
            self.assertEqual(prep[3]['text'], next_page_text)
            self.assertEqual(prep[3]['url'], '/page/2/')
            self.assertFalse(prep[3]['active'])

            del page, prep

            page = pagin.page(2)
            prep = pagination._prepare(page, 'page')
            self.assertEqual(len(prep), 5)
            self.assertEqual(prep[0]['text'], prev_page_text)
            self.assertEqual(prep[0]['url'], '/page/1/')
            self.assertFalse(prep[0]['active'])
            self.assertEqual(prep[1]['text'], '1')
            self.assertEqual(prep[1]['url'], '/page/1/')
            self.assertFalse(prep[1]['active'])
            self.assertEqual(prep[2]['text'], '2')
            self.assertEqual(prep[2]['url'], '#')
            self.assertTrue(prep[2]['active'])
            self.assertEqual(prep[3]['text'], '3')
            self.assertEqual(prep[3]['url'], '/page/3/')
            self.assertFalse(prep[3]['active'])
            self.assertEqual(prep[4]['text'], next_page_text)
            self.assertEqual(prep[4]['url'], '/page/3/')
            self.assertFalse(prep[4]['active'])

            del page, prep

            page = pagin.page(3)
            prep = pagination._prepare(page, 'page')
            self.assertEqual(len(prep), 4)
            self.assertEqual(prep[0]['text'], prev_page_text)
            self.assertEqual(prep[0]['url'], '/page/2/')
            self.assertFalse(prep[0]['active'])
            for i in range(1, 3):
                self.assertEqual(prep[i]['text'], str(i + 1))
                self.assertEqual(prep[i]['url'], '/page/{0}/'.format(i + 1))
                self.assertFalse(prep[i]['active'])

            del page, prep

        """
        """
        --- Всего страниц: 3, показывать соседей: 20 ---
        1: <1> 2 3 >>
        2: << 1 <2> 3 >>
        3: << 1 2 <3>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            page3_20_1 = pagin.page(1)
            page3_20_2 = pagin.page(2)
            page3_20_3 = pagin.page(3)

        """
        ------ Всего страниц: 4, показывать соседей: 1 ------
        1: <1> 2 >> 4
        2: << 1 <2> 3 >> 4
        3: 1 << 2 <3> 4 >>
        4: 1 << 3 <4>
        """
        tl4 = [1, 2, 3, 4, ]
        pagin4 = paginator.Paginator(tl4, 1)

        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            page4_1_1 = pagin4.page(1)
            page4_1_2 = pagin4.page(2)
            page4_1_3 = pagin4.page(3)
            page4_1_4 = pagin4.page(4)

        """
        --- Всего страниц: 4, показывать соседей: 2 ---
        1: <1> 2 3 >> 4
        2: << 1 <2> 3 4 >>
        3: << 1 2 <3> 4 >>
        4: 1 << 2 3 <4>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            page4_2_1 = pagin4.page(1)
            page4_2_2 = pagin4.page(2)
            page4_2_3 = pagin4.page(3)
            page4_2_4 = pagin4.page(4)

        """
        --- Всего страниц: 4, показывать соседей: 20 ---
        1: <1> 2 3 4 >>
        2: << 1 <2> 3 4 >>
        3: << 1 2 <3> 4 >>
        4: << 1 2 3 <4>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            page4_20_1 = pagin4.page(1)
            page4_20_2 = pagin4.page(2)
            page4_20_3 = pagin4.page(3)
            page4_20_4 = pagin4.page(4)

        """
        ------ Всего страниц: 5, показывать соседей: 1 ------
        1: <1> 2 >> 5
        2: << 1 <2> 3 >> 5
        3: 1 << 2 <3> 4 >> 5
        4: 1 << 3 <4> 5 >>
        5: 1 << 4 <5>
        """
        tl5 = [1, 2, 3, 4, 5, ]
        pagin5 = paginator.Paginator(tl5, 1)

        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            page5_1_1 = pagin5.page(1)
            page5_1_2 = pagin5.page(2)
            page5_1_3 = pagin5.page(3)
            page5_1_4 = pagin5.page(4)
            page5_1_5 = pagin5.page(5)

        """
        --- Всего страниц: 5, показывать соседей: 2 ---
        1: <1> 2 3 >> 5
        2: << 1 <2> 3 4 >> 5
        3: << 1 2 <3> 4 5 >>
        4: 1 << 2 3 <4> 5 >>
        5: 1 << 3 4 <5>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            page5_2_1 = pagin5.page(1)
            page5_2_2 = pagin5.page(2)
            page5_2_3 = pagin5.page(3)
            page5_2_4 = pagin5.page(4)
            page5_2_5 = pagin5.page(5)

        """
        --- Всего страниц: 5, показывать соседей: 20 ---
        1: <1> 2 3 4 5 >>
        2: << 1 <2> 3 4 5 >>
        3: << 1 2 <3> 4 5 >>
        4: << 1 2 3 <4> 5 >>
        5: << 1 2 3 3 4 <5>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            page5_20_1 = pagin5.page(1)
            page5_20_2 = pagin5.page(2)
            page5_20_3 = pagin5.page(3)
            page5_20_4 = pagin5.page(4)
            page5_20_5 = pagin5.page(5)

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
        tl10 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ]
        pagin10 = paginator.Paginator(tl10, 1)

        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            page10_1_1 = pagin10.page(1)
            page10_1_2 = pagin10.page(2)
            page10_1_3 = pagin10.page(3)
            page10_1_4 = pagin10.page(4)
            page10_1_5 = pagin10.page(5)
            page10_1_6 = pagin10.page(6)
            page10_1_7 = pagin10.page(7)
            page10_1_8 = pagin10.page(8)
            page10_1_9 = pagin10.page(9)
            page10_1_10 = pagin10.page(10)

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
            page10_2_1 = pagin10.page(1)
            page10_2_2 = pagin10.page(2)
            page10_2_3 = pagin10.page(3)
            page10_2_4 = pagin10.page(4)
            page10_2_5 = pagin10.page(5)
            page10_2_6 = pagin10.page(6)
            page10_2_7 = pagin10.page(7)
            page10_2_8 = pagin10.page(8)
            page10_2_9 = pagin10.page(9)
            page10_2_10 = pagin10.page(10)

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
            page10_20_1 = pagin10.page(1)
            page10_20_2 = pagin10.page(2)
            page10_20_3 = pagin10.page(3)
            page10_20_4 = pagin10.page(4)
            page10_20_5 = pagin10.page(5)
            page10_20_6 = pagin10.page(6)
            page10_20_7 = pagin10.page(7)
            page10_20_8 = pagin10.page(8)
            page10_20_9 = pagin10.page(9)
            page10_20_10 = pagin10.page(10)