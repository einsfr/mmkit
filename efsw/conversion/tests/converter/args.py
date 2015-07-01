from django.test import TestCase

from efsw.conversion.converter.args import *


class WrongClass:
    pass


class ArgumentsBuilderTestCase(TestCase):

    DEFAULT_ARGS = ['-hide_banner', '-n', '-nostdin']

    def test_wrong_add_type(self):
        ab = ArgumentsBuilder()
        with self.assertRaises(TypeError):
            ab.add_input('wrong_type')
        with self.assertRaises(TypeError):
            ab.add_output('wrong_type')

    def test_empty(self):
        ab = ArgumentsBuilder()
        with self.assertRaises(ConvArgsException):
            ab.build(IOPathConfiguration())
        ab.add_input(Input())
        with self.assertRaises(ConvArgsException):
            ab.build(IOPathConfiguration)

    def test_wrong_io_path_type(self):
        ab = ArgumentsBuilder()
        ab.add_input(Input()).add_output(Output())
        with self.assertRaises(TypeError):
            ab.build('wrong_type')

    def test_build_simple(self):
        ab = ArgumentsBuilder()
        ab.add_input(Input()).add_output(Output())
        io_path_conf = IOPathConfiguration(['in_path'], ['out_path'])
        self.assertEqual(
            self.DEFAULT_ARGS + ['-i', 'in_path', 'out_path'],
            ab.build(io_path_conf)
        )
