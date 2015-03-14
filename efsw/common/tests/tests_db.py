from django.test import TestCase
from django.db import connection
from django.utils import timezone

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
        date_value = timezone.now()
        m.extra_data = {
            'name': 'test_name',
            'ch': 'some-char-data',
            'da': date_value,
        }
        m.save()
        m_id = m.id
        m = SimpleExtraDataModel.objects.get(pk=m_id)
        self.assertEqual(m.extra_data['ch'], 'some-char-data')
        self.assertEqual(m.extra_data['da'], date_value.date())
        self.assertNotIn('name', m.extra_data)