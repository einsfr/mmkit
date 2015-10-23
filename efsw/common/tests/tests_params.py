from django.test import TestCase

from efsw.common.utils import params


class ParamsTestCase(TestCase):

    def test_optional(self):
        self.assertEqual(
            {'a': '', 'b': 'b', 'c': ''},
            params.parse_params(
                {'a': '', 'b': 'b'},
                a=None, b=None, c=None
            )
        )

    def test_regular(self):
        self.assertEqual(
            {'a': '1234', 'b': 'abc def', 'c': ''},
            params.parse_params(
                {'a': '1234', 'b': 'abc def', 'c': ''},
                a=r'\d+', b=r'\w+ \w+', c=r'.*'
            )
        )

    def test_callable(self):
        self.assertEqual(
            {'a': 'abc123', 'b': None, 'c': '123'},
            params.parse_params(
                {'a': 'abc123', 'c': '123'},
                a=lambda x: x == 'abc123', b=lambda x: x is None, c=lambda x: x is None or x == '123'
            )
        )
