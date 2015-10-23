from django.test import TestCase
from django.db import connection, models

from efsw.common.db.models.ordered_model import OrderedModel


class SimpleOrderedModel(OrderedModel):

    class Meta:
        app_label = 'tests'


class AnotherOrderedModel(OrderedModel):

    class Meta:
        app_label = 'tests'


class DomainOrderedModel(OrderedModel):

    class Meta:
        app_label = 'tests'

    order_domain_field = 'domain'

    domain = models.PositiveIntegerField()


class OrderedModelTestCase(TestCase):

    def setUp(self):
        super().setUp()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(SimpleOrderedModel())
            schema_editor.create_model(DomainOrderedModel())

    def tearDown(self):
        super().tearDown()
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(SimpleOrderedModel())
            schema_editor.delete_model(DomainOrderedModel())

    def assertObjectsValuesEqual(self, check_list):
        self.assertEqual(
            check_list,
            list(SimpleOrderedModel.objects.all().order_by('id').values_list('id', 'order'))
        )

    def assertDomainObjectsValuesEqual(self, check_list):
        self.assertEqual(
            check_list,
            list(DomainOrderedModel.objects.all().order_by('id').values_list('id', 'order'))
        )

    def test_append(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        self.assertObjectsValuesEqual([(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), ])

    def test_append_domain(self):
        for i in range(0, 6):
            DomainOrderedModel(domain=1 if i % 2 == 0 else 2).save()
        self.assertDomainObjectsValuesEqual([(1, 0), (2, 0), (3, 1), (4, 1), (5, 2), (6, 2), ])

    def test_pk_not_set_empty_order_set(self):
        SimpleOrderedModel(order=5).save()
        self.assertObjectsValuesEqual([(1, 0), ])

    def test_pk_not_set_empty_order_set_domain(self):
        DomainOrderedModel(order=5, domain=1).save()
        DomainOrderedModel(order=5, domain=2).save()
        self.assertDomainObjectsValuesEqual([(1, 0), (2, 0)])

    def test_pk_not_set_order_exceeds(self):
        SimpleOrderedModel().save()
        SimpleOrderedModel(order=5).save()
        self.assertObjectsValuesEqual([(1, 0), (2, 1), ])

    def test_pk_not_set_order_exceeds_domain(self):
        DomainOrderedModel(domain=1).save()
        DomainOrderedModel(order=5, domain=1).save()
        DomainOrderedModel(domain=2).save()
        DomainOrderedModel(order=5, domain=2).save()
        self.assertDomainObjectsValuesEqual([(1, 0), (2, 1), (3, 0), (4, 1), ])

    def test_pk_not_set_insert(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        SimpleOrderedModel(order=0).save()
        self.assertObjectsValuesEqual([(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 0), ])
        SimpleOrderedModel(order=3).save()
        self.assertObjectsValuesEqual([(1, 1), (2, 2), (3, 4), (4, 5), (5, 6), (6, 0), (7, 3), ])

    def test_pk_not_set_insert_domain(self):
        for i in range(1, 7):
            DomainOrderedModel(domain=1 if i % 2 == 0 else 2).save()
        DomainOrderedModel(order=0, domain=1).save()
        self.assertDomainObjectsValuesEqual([(1, 0), (2, 1), (3, 1), (4, 2), (5, 2), (6, 3), (7, 0)])
        DomainOrderedModel(order=1, domain=2).save()
        self.assertDomainObjectsValuesEqual([(1, 0), (2, 1), (3, 2), (4, 2), (5, 3), (6, 3), (7, 0), (8, 1)])

    def test_pk_not_set_insert_below_min(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        SimpleOrderedModel(order=-3).save()
        self.assertObjectsValuesEqual([(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 0), ])

    def test_pk_not_set_insert_below_min_domain(self):
        for i in range(1, 7):
            DomainOrderedModel(domain=1 if i % 2 == 0 else 2).save()
        DomainOrderedModel(order=-3, domain=1).save()
        self.assertDomainObjectsValuesEqual([(1, 0), (2, 1), (3, 1), (4, 2), (5, 2), (6, 3), (7, 0)])

    def test_pk_set_insert(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        SimpleOrderedModel(pk=6, order=3).save()
        self.assertObjectsValuesEqual([(1, 0), (2, 1), (3, 2), (4, 4), (5, 5), (6, 3), ])

    def test_pk_set_insert_domain(self):
        for i in range(1, 7):
            DomainOrderedModel(domain=1 if i % 2 == 0 else 2).save()
        DomainOrderedModel(pk=7, order=1, domain=1).save()
        self.assertDomainObjectsValuesEqual([(1, 0), (2, 0), (3, 1), (4, 2), (5, 2), (6, 3), (7, 1)])

    def test_move_order_not_set(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        obj = SimpleOrderedModel.objects.get(pk=3)
        obj.order = None
        obj.save()
        self.assertObjectsValuesEqual([(1, 0), (2, 1), (3, 4), (4, 2), (5, 3), ])

    def test_move_order_not_set_domain(self):
        for i in range(1, 7):
            DomainOrderedModel(domain=1 if i % 2 == 0 else 2).save()
        obj = DomainOrderedModel.objects.get(pk=3)
        obj.order = None
        obj.save()
        self.assertDomainObjectsValuesEqual([(1, 0), (2, 0), (3, 2), (4, 1), (5, 1), (6, 2)])

    def test_move_right(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        obj = SimpleOrderedModel.objects.get(pk=3)
        obj.order = 7
        obj.save()
        self.assertObjectsValuesEqual([(1, 0), (2, 1), (3, 4), (4, 2), (5, 3), ])

    def test_move_right_domain(self):
        for i in range(1, 7):
            DomainOrderedModel(domain=1 if i % 2 == 0 else 2).save()
        obj = DomainOrderedModel.objects.get(pk=3)
        obj.order = 7
        obj.save()
        self.assertDomainObjectsValuesEqual([(1, 0), (2, 0), (3, 2), (4, 1), (5, 1), (6, 2)])

    def test_move_left(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        obj = SimpleOrderedModel.objects.get(pk=3)
        obj.order = 1
        obj.save()
        self.assertObjectsValuesEqual([(1, 0), (2, 2), (3, 1), (4, 3), (5, 4), ])

    def test_move_left_domain(self):
        for i in range(1, 7):
            DomainOrderedModel(domain=1 if i % 2 == 0 else 2).save()
        obj = DomainOrderedModel.objects.get(pk=3)
        obj.order = 0
        obj.save()
        self.assertDomainObjectsValuesEqual([(1, 1), (2, 0), (3, 0), (4, 1), (5, 2), (6, 2)])

    def test_delete(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        SimpleOrderedModel.objects.get(pk=3).delete()
        self.assertObjectsValuesEqual([(1, 0), (2, 1), (4, 2), (5, 3), ])

    def test_delete_domain(self):
        for i in range(0, 6):
            DomainOrderedModel(domain=1 if i % 2 == 0 else 2).save()
        DomainOrderedModel.objects.get(pk=3).delete()
        self.assertDomainObjectsValuesEqual([(1, 0), (2, 0), (4, 1), (5, 1), (6, 2)])
        DomainOrderedModel.objects.get(pk=4).delete()
        self.assertDomainObjectsValuesEqual([(1, 0), (2, 0), (5, 1), (6, 1)])

    def test_swap(self):
        for i in range(0, 5):
            SimpleOrderedModel().save()
        obj = SimpleOrderedModel.objects.get(pk=3)
        swap_obj = SimpleOrderedModel.objects.get(pk=5)
        obj.order_swap(swap_obj)
        self.assertObjectsValuesEqual([(1, 0), (2, 1), (3, 4), (4, 3), (5, 2), ])
        swap_obj = AnotherOrderedModel()
        with self.assertRaises(ValueError):
            obj.order_swap(swap_obj)
        swap_obj = SimpleOrderedModel()
        with self.assertRaises(ValueError):
            obj.order_swap(swap_obj)
        swap_obj = SimpleOrderedModel(pk=6)
        with self.assertRaises(ValueError):
            obj.order_swap(swap_obj)

    def test_swap_domain(self):
        for i in range(1, 7):
            DomainOrderedModel(domain=1 if i % 2 == 0 else 2).save()
        obj = DomainOrderedModel.objects.get(pk=3)
        swap_obj = DomainOrderedModel.objects.get(pk=4)
        with self.assertRaises(ValueError):
            obj.order_swap(swap_obj)
        swap_obj = DomainOrderedModel.objects.get(pk=5)
        obj.order_swap(swap_obj)
        self.assertDomainObjectsValuesEqual([(1, 0), (2, 0), (3, 2), (4, 1), (5, 1), (6, 2)])

    def test_order_check(self):
        disorder_list = [1, 1, 2, 2, 2, 3, 4, 6, 7, 7, 8, 8, 9, 10, 13, 14, 16, 20, 21, 22, 22]
        SimpleOrderedModel.objects.bulk_create([SimpleOrderedModel(order=o) for o in disorder_list])
        SimpleOrderedModel.order_check()
        self.assertEqual(
            list(SimpleOrderedModel.objects.order_by('order').values_list('order', flat=True)),
            list(range(0, len(disorder_list)))
        )

    def test_order_check_domain(self):
        disorder_list = [(1, 1), (1, 1), (1, 2), (2, 2), (3, 1), (2, 1), (4, 1), (4, 1), (4, 2), (5, 1), (6, 2), (8, 2)]
        DomainOrderedModel.objects.bulk_create([DomainOrderedModel(order=o, domain=d) for o, d in disorder_list])
        DomainOrderedModel.order_check()
        self.assertEqual(
            list(DomainOrderedModel.objects.order_by('id').values_list('order', flat=True)),
            [1, 0, 0, 1, 3, 2, 5, 4, 2, 6, 3, 4]
        )
