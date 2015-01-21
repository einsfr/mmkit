from django.test import TestCase
from django.db import models

from efsw.common.templatetags import model


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

    def test_verbose_name(self):
        not_instance = self.NotModel()
        self.assertEqual(model.verbose_name(not_instance), '')
        self.assertEqual(model.verbose_name(not_instance, False), '')
        self.assertEqual(model.verbose_name(not_instance, True), '')
        instance = self.TestModel()
        self.assertEqual(model.verbose_name(instance), 'тестомодель')
        self.assertEqual(model.verbose_name(instance, False), 'тестомодель')
        self.assertEqual(model.verbose_name(instance, True), 'тестомодели')
        instance_wo = self.TestModelWithoutVerbose()
        self.assertEqual(model.verbose_name(instance_wo), 'test model without verbose')
        self.assertEqual(model.verbose_name(instance_wo, False), 'test model without verbose')
        self.assertEqual(model.verbose_name(instance_wo, True), 'test model without verboses')

    def test_field_verbose_name(self):
        not_instance = self.NotModel()
        self.assertEqual(model.field_verbose_name(not_instance, 'name'), '')
        self.assertEqual(model.field_verbose_name(not_instance, 'non-exist'), '')
        instance = self.TestModel()
        self.assertEqual(model.field_verbose_name(instance, 'name'), 'тестовое имя')
        self.assertEqual(model.field_verbose_name(instance, 'non-exist'), '')
        instance_wo = self.TestModelWithoutVerbose()
        self.assertEqual(model.field_verbose_name(instance_wo, 'name'), 'name')
        self.assertEqual(model.field_verbose_name(instance_wo, 'non-exist'), '')