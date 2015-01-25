from django.test import TestCase
from django.db import models
from django.core import paginator

from efsw.common.templatetags import model
from efsw.common.templatetags import pagination


class TemplateTagsTestCase(TestCase):

    class TestModel(models.Model):

        class Meta:
            verbose_name='тестомодель'
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

    def test_pagination(self):
        """ Тесты для листалки """

        """
        ------ Всего страниц: 1, показывать соседей: 1 ------
        1: <1>
        """
        tl1 = [1, ]

        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            pass

        """
        --- Всего страниц: 1, показывать соседей: 2 ---
        1: <1>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            pass

        """
        --- Всего страниц: 1, показывать соседей: 20 ---
        1: <1>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            pass

        """
        ------ Всего страниц: 2, показывать соседей: 1 ------
        1: <1> 2 >>
        2: << 1 <2>
        """
        tl2 = [1, 2, ]

        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            pass

        """
        --- Всего страниц: 2, показывать соседей: 2 ---
        1: <1> 2 >>
        2: << 1 <2>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            pass

        """
        --- Всего страниц: 2, показывать соседей: 20 ---
        1: <1> 2 >>
        2: << 1 <2>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            pass

        """
        ------ Всего страниц: 3, показывать соседей: 1 ------
        1: <1> 2 >> 3
        2: << 1 <2> 3 >>
        3: 1 << 2 <3>
        """
        tl3 = [1, 2, 3, ]

        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            pass

        """
        --- Всего страниц: 3, показывать соседей: 2 ---
        1: <1> 2 3 >>
        2: << 1 <2> 3 >>
        3: << 1 2 <3>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            pass

        """
        --- Всего страниц: 3, показывать соседей: 20 ---
        1: <1> 2 3 >>
        2: << 1 <2> 3 >>
        3: << 1 2 <3>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            pass

        """
        ------ Всего страниц: 4, показывать соседей: 1 ------
        1: <1> 2 >> 4
        2: << 1 <2> 3 >> 4
        3: 1 << 2 <3> 4 >>
        4: 1 << 3 <4>
        """
        tl4 = [1, 2, 3, 4, ]

        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            pass

        """
        --- Всего страниц: 4, показывать соседей: 2 ---
        1: <1> 2 3 >> 4
        2: << 1 <2> 3 4 >>
        3: << 1 2 <3> 4 >>
        4: 1 << 2 3 <4>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            pass

        """
        --- Всего страниц: 4, показывать соседей: 20 ---
        1: <1> 2 3 4 >>
        2: << 1 <2> 3 4 >>
        3: << 1 2 <3> 4 >>
        4: << 1 2 3 <4>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            pass

        """
        ------ Всего страниц: 5, показывать соседей: 1 ------
        1: <1> 2 >> 5
        2: << 1 <2> 3 >> 5
        3: 1 << 2 <3> 4 >> 5
        4: 1 << 3 <4> 5 >>
        5: 1 << 4 <5>
        """
        tl5 = [1, 2, 3, 4, 5, ]

        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            pass

        """
        --- Всего страниц: 5, показывать соседей: 2 ---
        1: <1> 2 3 >> 5
        2: << 1 <2> 3 4 >> 5
        3: << 1 2 <3> 4 5 >>
        4: 1 << 2 3 <4> 5 >>
        5: 1 << 3 4 <5>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            pass

        """
        --- Всего страниц: 5, показывать соседей: 20 ---
        1: <1> 2 3 4 5 >>
        2: << 1 <2> 3 4 5 >>
        3: << 1 2 <3> 4 5 >>
        4: << 1 2 3 <4> 5 >>
        5: << 1 2 3 3 4 <5>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            pass

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

        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            pass

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
            pass

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
            pass