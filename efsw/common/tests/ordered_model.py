from django.test import TestCase
from django.db import connection

from efsw.common.db.models.ordered_model import OrderedModel


class SimpleOrderedModel(OrderedModel):
    pass


class OrderedModelTestCase(TestCase):

    def setUp(self):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(SimpleOrderedModel())

    def tearDown(self):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(SimpleOrderedModel())

    def assertObjectsValuesEqual(self, check_list):
        self.assertEqual(
            check_list,
            list(SimpleOrderedModel.objects.all().values_list('id', 'order'))
        )

    def test_append(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        self.assertObjectsValuesEqual([(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), ])

    def test_pk_not_set_empty_order_set(self):
        SimpleOrderedModel(order=5).save()
        self.assertObjectsValuesEqual([(1, 0), ])

    def test_pk_not_set_order_exceeds(self):
        SimpleOrderedModel().save()
        SimpleOrderedModel(order=5).save()
        self.assertObjectsValuesEqual([(1, 0), (2, 1), ])

    def test_pk_not_set_insert(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        SimpleOrderedModel(order=0).save()
        self.assertObjectsValuesEqual([(6, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
        SimpleOrderedModel(order=3).save()
        self.assertObjectsValuesEqual([(6, 0), (1, 1), (2, 2), (7, 3), (3, 4), (4, 5), (5, 6)])

    def test_pk_not_set_insert_below_min(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        SimpleOrderedModel(order=-3).save()
        self.assertObjectsValuesEqual([(6, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])

    def test_pk_set_insert(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        SimpleOrderedModel(pk=6, order=3).save()
        self.assertObjectsValuesEqual([(1, 0), (2, 1), (3, 2), (6, 3), (4, 4), (5, 5)])
