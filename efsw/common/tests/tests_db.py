from decimal import Decimal
import uuid

from django.test import TestCase
from django.db import connection
from django.utils import timezone
from django.core import exceptions

from efsw.common.tests.models import SimpleExtraDataModel, AllFieldsExtraDataModel


class ExtraDataModelTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.schema_editor() as se:
            se.create_model(SimpleExtraDataModel())
            se.create_model(AllFieldsExtraDataModel())

    def testModelCreation(self):
        m = SimpleExtraDataModel()
        date_value = timezone.now().date()
        m.extra_data = {
            'name': 'test_name',
            'ch': 'some-char-data',
            'da': date_value,
        }
        m.save()
        m_id = m.id
        m = SimpleExtraDataModel.objects.get(pk=m_id)
        self.assertEqual(m.extra_data['ch'], 'some-char-data')
        self.assertEqual(m.extra_data['da'], date_value)
        self.assertNotIn('name', m.extra_data)
        m = SimpleExtraDataModel()
        m.save()
        m_id = m.id
        m = SimpleExtraDataModel.objects.get(pk=m_id)
        self.assertEqual(m.extra_data, {})

    def testFieldCompatibility(self):
        fields = {
            'bigint': {
                'valid': [
                    (9223372036854775807, ),
                    (-9223372036854775808, ),
                ],
                'invalid': [
                    9223372036854775808
                ]
            },
            'bool': {
                'valid': [
                    (True, ),
                    (False, )
                ],
                'invalid': [
                    'non-bool'
                ]
            },
            'char': {
                'valid': [
                    ('asfasd', ),
                    ('adfgdfag asdgfads', )
                ],
                'invalid': [
                    'a' * 33
                ]
            },
            'date': {
                'valid': [
                    (timezone.now().date(), )
                ],
                'invalid': [
                    'non-date-value'
                ]
            },
            'decimal': {
                'valid': [
                    (123.45, Decimal('123.45'))
                ],
                'invalid': [
                    'non-decimal-value'
                ]
            },
            'email': {
                'valid': [
                    ('example@example.com', )
                ],
                'invalid': [
                    'example@example'
                ]
            },
            'float': {
                'valid': [
                    (1234.5678, )
                ],
                'invalid': [
                    'non-float-value'
                ]
            },
            'int': {
                'valid': [
                    (12345, )
                ],
                'invalid': [
                    'non-integer-value'
                ]
            },
            'ipaddr': {
                'valid': [
                    ('192.168.1.1', )
                ],
                'invalid': [
                    'non-ip-value'
                ]
            },
            'nullbool': {
                'valid': [
                    (True, ),
                    (False, ),
                    (None, )
                ],
                'invalid': [
                    'non-bool-value'
                ]
            },
            'posint': {
                'valid': [
                    (12345, )
                ],
                'invalid': [
                    -12345,
                    'non-integer-value'
                ]
            },
            'possmint': {
                'valid': [
                    (12345, )
                ],
                'invalid': [
                    -12345,
                    'non-integer-value',
                ]
            },
            'slug': {
                'valid': [
                    ('ads5426_-', )
                ],
                'invalid': [
                    'invalid-slug-,%&'
                ]
            },
            'smint': {
                'valid': [
                    (123, ),
                    (-123, )
                ],
                'invalid': [
                    'non-integer',
                ]
            },
            'text': {
                'valid': [
                    ('some-not-very-long-text-data', ),
                ],
                'invalid': [
                ]
            },
            'time': {
                'valid': [
                    (timezone.now().time(), )
                ],
                'invalid': [
                    'not-time-value',
                ]
            },
            'url': {
                'valid': [
                    ('http://example.com/example?example=example', ),
                ],
                'invalid': [
                    'not-a-url'
                ]
            },
            'uuid': {
                'valid': [
                    (uuid.uuid4(), )
                ],
                'invalid': [
                    'not-a-uuid'
                ]
            }
        }

        for f_name, f_dict in fields.items():
            print('Testing {0}'.format(type(AllFieldsExtraDataModel.get_extra_fields_mapping()[f_name])))
            for f_tuple in f_dict['valid']:
                m = AllFieldsExtraDataModel()
                m.extra_data = dict([(f_name, f_tuple[0])])
                m.save()
                m_id = m.id
                m = AllFieldsExtraDataModel.objects.get(pk=m_id)
                if len(f_tuple) == 1:
                    self.assertEqual(m.extra_data[f_name], f_tuple[0])
                else:
                    self.assertEqual(m.extra_data[f_name], f_tuple[1])
            for f_value in f_dict['invalid']:
                m = AllFieldsExtraDataModel()
                m.extra_data = dict([(f_name, f_value)])
                with self.assertRaises(exceptions.ValidationError):
                    m.save()
            print('OK')