from django.test import TestCase

from efsw.conversion.converter.args import *


class WrongClass:
    pass


class ArgumentsBuilderTestCase(TestCase):

    DEFAULT_ARGS = ['-hide_banner', '-n', '-nostdin']

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
            self.DEFAULT_ARGS + ['-i', 'in_path', 'out_path'],
            ab.build()
        )
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path', [('-r', '25')]))
        ab.add_output(Output('out_path', [('-r', '25')]))
        self.assertEqual(
            self.DEFAULT_ARGS + ['-r', '25', '-i', 'in_path', '-r', '25', 'out_path'],
            ab.build()
        )

    def test_c(self):
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path').c('codec')).add_output(Output('out_path'))
        self.assertEqual(
            self.DEFAULT_ARGS + ['-c', 'codec', '-i', 'in_path', 'out_path'],
            ab.build()
        )
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path')).add_output(Output('out_path').c('codec'))
        self.assertEqual(
            self.DEFAULT_ARGS + ['-i', 'in_path', '-c', 'codec', 'out_path'],
            ab.build()
        )
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path')).add_output(Output('out_path').c('codec', 'v:0'))
        self.assertEqual(
            self.DEFAULT_ARGS + ['-i', 'in_path', '-c:v:0', 'codec', 'out_path'],
            ab.build()
        )
        ab = ArgumentsBuilder()
        with self.assertRaises(ValueError):
            ab.add_input(Input('in_path')).add_output(Output('out_path').c('codec', 'wrong_id'))

    def test_f(self):
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path').f('test_format')).add_output(Output('out_path'))
        self.assertEqual(
            self.DEFAULT_ARGS + ['-f', 'test_format', '-i', 'in_path', 'out_path'],
            ab.build()
        )

    def test_t(self):
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path')).add_output(Output('out_path').t('01:00:02'))
        self.assertEqual(
            self.DEFAULT_ARGS + ['-i', 'in_path', '-t', '01:00:02', 'out_path'],
            ab.build()
        )
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path')).add_output(Output('out_path').t('00:02'))
        self.assertEqual(
            self.DEFAULT_ARGS + ['-i', 'in_path', '-t', '00:02', 'out_path'],
            ab.build()
        )
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path')).add_output(Output('out_path').t('28'))
        self.assertEqual(
            self.DEFAULT_ARGS + ['-i', 'in_path', '-t', '28', 'out_path'],
            ab.build()
        )
        ab = ArgumentsBuilder()
        with self.assertRaises(ValueError):
            ab.add_input(Input('in_path')).add_output(Output('out_path').t('wrong_duration'))

    def test_ss(self):
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path')).add_output(Output('out_path').ss('01:00:02'))
        self.assertEqual(
            self.DEFAULT_ARGS + ['-i', 'in_path', '-ss', '01:00:02', 'out_path'],
            ab.build()
        )
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path')).add_output(Output('out_path').ss('00:02'))
        self.assertEqual(
            self.DEFAULT_ARGS + ['-i', 'in_path', '-ss', '00:02', 'out_path'],
            ab.build()
        )
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path')).add_output(Output('out_path').ss('28'))
        self.assertEqual(
            self.DEFAULT_ARGS + ['-i', 'in_path', '-ss', '28', 'out_path'],
            ab.build()
        )
        ab = ArgumentsBuilder()
        with self.assertRaises(ValueError):
            ab.add_input(Input('in_path')).add_output(Output('out_path').ss('wrong_duration'))

    def test_itsoffset(self):
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path').itsoffset('01:00:02')).add_output(Output('out_path'))
        self.assertEqual(
            self.DEFAULT_ARGS + ['-itsoffset', '01:00:02', '-i', 'in_path', 'out_path'],
            ab.build()
        )
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path').itsoffset('-00:02')).add_output(Output('out_path'))
        self.assertEqual(
            self.DEFAULT_ARGS + ['-itsoffset', '-00:02', '-i', 'in_path', 'out_path'],
            ab.build()
        )
        ab = ArgumentsBuilder()
        ab.add_input(Input('in_path').itsoffset('297')).add_output(Output('out_path'))
        self.assertEqual(
            self.DEFAULT_ARGS + ['-itsoffset', '297', '-i', 'in_path', 'out_path'],
            ab.build()
        )
