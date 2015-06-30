import re
import shlex

from efsw.conversion.converter.exceptions import ConvArgsException

def _build_options(options):
    result = []
    for o in options:
        if type(o) == tuple:
            result.extend(o)
        else:
            result.append(o)
    return result


class OptionsHandler:

    def __init__(self, options=None):
        self._options = list(options) if options is not None else []

    def set_option(self, option):
        self._options.append(option)
        return self

    def set_option_value(self, option, value):
        self._options.append((option, value))
        return self

    def del_option(self, option):
        for i, v in enumerate(self._options):
            if v == option:
                del(self._options[i])
                return self
            try:
                if v[0] == option:
                    del(self._options[i])
                    return self
            except TypeError:
                continue


class ArgumentsBuilder(OptionsHandler):

    DEFAULT_CONVERT_ARGS = ['-hide_banner', '-n', '-nostdin']

    INFO_OPTIONS = (
        '-L', '-h', '-version', '-formats', '-devices', '-codecs', '-decoders', '-encoders', '-bsfs', '-protocols',
        '-filters', '-pix_fmts', '-sample_fmts', '-layouts', '-colors', '-sources', '-sinks', '-opencl_bench'
    )

    GLOBAL_OPTIONS = (

    )

    def __init__(self, options=None):
        super().__init__(options)
        self._inputs_list = []
        self._outputs_list = []

    def add_input(self, in_obj):
        if not isinstance(in_obj, Input):
            raise TypeError('Неправильный тип аргумента - передано: "{0}", ожидалось: '
                            '"efsw.conversion.converter.args.Input".'.format(type(in_obj)))
        self._inputs_list.append(in_obj)
        return self

    def add_output(self, out_obj):
        if not isinstance(out_obj, Output):
            raise TypeError('Неправильный тип аргумента - передано: "{0}", ожидалось: '
                            '"efsw.conversion.converter.args.Output".'.format(type(out_obj)))
        self._outputs_list.append(out_obj)
        return self

    def build(self, override_defaults=False):
        if not self._inputs_list:
            raise ConvArgsException('Не задано ни одного входа.')
        if not self._outputs_list:
            raise ConvArgsException('Не задано ни одного выхода.')
        if self._options is None:
            args = self.DEFAULT_CONVERT_ARGS
        elif self._options is not None and not override_defaults:
            args = self.DEFAULT_CONVERT_ARGS + _build_options(self._options)
        else:
            args = _build_options(self._options)
        for i in self._inputs_list:
            args.extend(i.build())
        for o in self._outputs_list:
            args.extend(o.build())
        return args

    @classmethod
    def from_string(cls, args_string):
        args_list = shlex.split(args_string)


class InputOutputAbstract(OptionsHandler):

    def __init__(self, path, options=None):
        super().__init__(options)
        if not path:
            raise ValueError('Путь в аргументе path не может быть пустым.')
        self.path = path

    def f(self, format_str):
        return self.set_option_value('-f', format_str)

    @staticmethod
    def _check_stream_id(stream_id):

        def _is_int(i):
            try:
                int(i)
                return True
            except ValueError:
                return False

        if _is_int(stream_id):
            return True
        splitted_id = str(stream_id).split(':')
        l = len(splitted_id)
        if l == 1:
            if splitted_id[0] in ['v', 'a', 's', 'd', 't', 'u']:
                return True
            if splitted_id[0][0] == '#' and len(splitted_id[0]) > 1 and _is_int(splitted_id[0][1:]):
                return True
            return False
        elif l == 2:
            if splitted_id[0] in ['v', 'a', 's', 'd', 't', 'p', 'i'] and _is_int(splitted_id[1]):
                return True
            if splitted_id[0] == 'm':
                return True
        elif l == 3:
            if splitted_id[0] == 'p' and _is_int(splitted_id[1]) and _is_int(splitted_id[2]):
                return True
            if splitted_id[0] == 'm':
                return True
        return False

    def c(self, codec_str, stream_id=None):
        if stream_id is not None and not self._check_stream_id(stream_id):
            raise ValueError('Неправильный формат идентификатора потока.')
        return self.set_option_value(
            '-c' if stream_id is None else '-c:{0}'.format(stream_id),
            codec_str
        )

    def codec(self, *args, **kwargs):
        return self.c(*args, **kwargs)

    def t(self, duration):
        if re.match(r'^(?:\d{2,}:)?[0-5][0-9]:[0-5][0-9](?:\.\d+)?$', duration) is None \
                and re.match(r'^\d+(?:\.\d+)?$', duration) is None:
            raise ValueError('Длительность потока должна быть указана в формате "[HH:]MM:SS[.mmm]" или "S+[.mmm]".')
        return self.set_option_value('-t', duration)

    def ss(self, position):
        if re.match(r'^(?:\d{2,}:)?[0-5][0-9]:[0-5][0-9](?:\.\d+)?$', position) is None \
                and re.match(r'^\d+(?:\.\d+)?$', position) is None:
            raise ValueError('Позиция в потоке должна быть указана в формате "[HH:]MM:SS[.mmm]" или "S+[.mmm]".')
        return self.set_option_value('-ss', position)

    def build(self):
        raise NotImplementedError


class Input(InputOutputAbstract):

    def build(self):
        return _build_options(self._options) + ['-i', self.path]

    def itsoffset(self, offset):
        if re.match(r'^-?(?:\d{2}:)?[0-5][0-9]:[0-5][0-9](?:\.\d+)?$', offset) is None \
                and re.match(r'^-?\d+(?:\.\d+)?$', offset) is None:
            raise ValueError('Смещение должно быть указано в формате "[-][HH:]MM:SS[.mmm]" или "[-]S+[.mmm]".')
        return self.set_option_value('-itsoffset', offset)


class Output(InputOutputAbstract):

    def build(self):
        return _build_options(self._options) + [self.path]
