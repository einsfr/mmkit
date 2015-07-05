from django.test import TestCase
from django.db import connection

from efsw.common.db.models.ordered_model import OrderedModel


class SimpleOrderedModel(OrderedModel):
    pass


class AnotherOrderedModel(OrderedModel):
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

    def test_move_order_not_set(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        obj = SimpleOrderedModel.objects.get(pk=3)
        obj.order = None
        obj.save()
        self.assertObjectsValuesEqual([(1, 0), (2, 1), (4, 2), (5, 3), (3, 4), ])

    def test_move_right(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        obj = SimpleOrderedModel.objects.get(pk=3)
        obj.order = 7
        obj.save()
        self.assertObjectsValuesEqual([(1, 0), (2, 1), (4, 2), (5, 3), (3, 4), ])

    def test_move_left(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        obj = SimpleOrderedModel.objects.get(pk=3)
        obj.order = 1
        obj.save()
        self.assertObjectsValuesEqual([(1, 0), (3, 1), (2, 2), (4, 3), (5, 4), ])

    def test_delete(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        SimpleOrderedModel.objects.get(pk=3).delete()
        self.assertObjectsValuesEqual([(1, 0), (2, 1), (4, 2), (5, 3), ])

    def test_swap(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        obj = SimpleOrderedModel.objects.get(pk=3)
        swap_obj = SimpleOrderedModel.objects.get(pk=5)
        obj.order_swap(swap_obj)
        self.assertObjectsValuesEqual([(1, 0), (2, 1), (5, 2), (4, 3), (3, 4), ])
        swap_obj = AnotherOrderedModel()
        with self.assertRaises(ValueError):
            obj.order_swap(swap_obj)
        swap_obj = SimpleOrderedModel()
        with self.assertRaises(ValueError):
            obj.order_swap(swap_obj)
        swap_obj = SimpleOrderedModel(pk=6)
        with self.assertRaises(ValueError):
            obj.order_swap(swap_obj)

    def test_order_check(self):
        disorder_list = [1, 1, 2, 2, 2, 3, 4, 6, 7, 7, 8, 8, 9, 10, 13, 14, 16, 20, 21, 22, 22]
        SimpleOrderedModel.objects.bulk_create([SimpleOrderedModel(order=o) for o in disorder_list])
        SimpleOrderedModel.order_check()
        self.assertEqual(
            list(SimpleOrderedModel.objects.order_by('order').values_list('order', flat=True)),
            list(range(0, len(disorder_list)))
        )
