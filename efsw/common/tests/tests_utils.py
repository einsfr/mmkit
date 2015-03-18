from django.test import TestCase

from efsw.common.utils import urlformatter


class UrlFormatterTestCase(TestCase):

    def test_wrong_format(self):
        input_list = [
            'smb:/host\\path/to\\file',
            'cifs://username@/path/'
        ]
        for i in input_list:
            print('Checking "{0}"...'.format(i))
            with self.assertRaises(urlformatter.WrongUrlFormatException):
                print(urlformatter.format_url(i))
            print('Wrong format, OK')

    def test_right_format(self):
        input_list = [
            ('smb://host/path\\to\\directory', 'smb://host/path/to/directory'),
            ('http://user@host/path/to/page', 'http://user@host/path/to/page'),
            ('ftp://user:password@host/path/to/file', 'ftp://user:password@host/path/to/file')
        ]
        for i in input_list:
            print('Checking "{0}"...'.format(i[0]))
            self.assertEqual(i[1], str(urlformatter.format_url(i[0])))
            print('Right format, OK')

    def test_format_win(self):
        self.assertEqual(
            '\\\\host\\path\\to\\directory',
            urlformatter.format_url('smb://host/path/to/directory').format_win()
        )
        self.assertEqual(
            '\\\\host\\path\\to\\directory',
            urlformatter.format_url('cifs://host/path/to/directory').format_win()
        )