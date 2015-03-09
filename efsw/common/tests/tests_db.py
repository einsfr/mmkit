from django.test import TestCase
from django.db import connection

from efsw.common.tests.models import SimpleExtraDataModel


class ExtraDataModelTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        model = SimpleExtraDataModel()
        with connection.schema_editor() as se:
            se.create_model(model)

    def testModelCreation(self):
        m = SimpleExtraDataModel()
        m.extra_data = {
            'name': 'test_name',
            'age': '25'
        }
        m.save()
        m_id = m.id
        m = SimpleExtraDataModel.objects.get(pk=m_id)
        self.assertEqual(m.extra_data['name'], 'test_name')
        self.assertEqual(m.extra_data['age'], '25')