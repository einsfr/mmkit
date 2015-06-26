from django.test import TestCase

from efsw.conversion.converter.args import *


class WrongClass:
    pass


class ArgumentsBuilderTestCase(TestCase):

    def test_wrong_class(self):
        ab = ArgumentsBuilder()
        with self.assertRaises(TypeError):
            ab.add_input(WrongClass())
        with self.assertRaises(TypeError):
            ab.add_output(WrongClass())

    def test_empty_constructors(self):
        with self.assertRaises(ValueError):
            i = Input('')
        with self.assertRaises(ValueError):
            o = Output('')

    def test_wrong_options(self):
        with self.assertRaises(TypeError):
            i = Input('path', 1)
        with self.assertRaises(TypeError):
            o = Output('path', 1)

    def test_simple(self):
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path')).add_output(Output('out_path'))
        self.assertEqual(
            ['-hide_banner', '-n', '-nostdin', '-i', 'in_path', 'out_path'],
            ab.build()
        )
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path', [('-r', '25')]))
        ab.add_output(Output('out_path', [('-r', '25')]))
        self.assertEqual(
            ['-hide_banner', '-n', '-nostdin', '-r', '25', '-i', 'in_path', '-r', '25', 'out_path'],
            ab.build()
        )

    def test_format(self):
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path').f('test_format')).add_output(Output('out_path'))
        self.assertEqual(
            ['-hide_banner', '-n', '-nostdin', '-f', 'test_format', '-i', 'in_path', 'out_path'],
            ab.build()
        )
