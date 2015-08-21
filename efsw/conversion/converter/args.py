import re
import copy

from efsw.conversion.converter.exceptions import ConvArgsException, IOPathResolveException


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

    def __init__(self, in_objects=None, out_objects=None, options=None):

        def _check_in_type(i):
            if not isinstance(i, Input):
                raise TypeError('Все элементы, входящие в состав аргумента in_objects должны быть экземплярами класса '
                                'Input.')
            return i

        def _check_out_type(o):
            if not isinstance(o, Output):
                raise TypeError('Все элементы, входящие в состав аргумента out_objects должны быть экземплярами класса '
                                'Output.')
            return o

        super().__init__(options)
        self._inputs = [] if in_objects is None else list(map(_check_in_type, in_objects))
        self._outputs = [] if out_objects is None else list(map(_check_out_type, out_objects))

    def __str__(self):
        io_path_conf = IOPathConfiguration(
            ['<input{0}>'.format(x) for x in range(0, len(self._inputs))],
            ['<output{0}>'.format(x) for x in range(0, len(self._outputs))]
        )
        return ' '.join(self.build(io_path_conf))

    def add_input(self, in_obj=None):
        if in_obj is not None and not isinstance(in_obj, Input):
            raise TypeError('Неправильный тип аргумента - передано: "{0}", ожидалось: '
                            '"efsw.conversion.converter.args.Input".'.format(type(in_obj)))
        self._inputs.append(in_obj if in_obj is not None else Input())
        return self

    @property
    def inputs(self):
        return copy.deepcopy(self._inputs)

    def add_output(self, out_obj=None):
        if out_obj is not None and not isinstance(out_obj, Output):
            raise TypeError('Неправильный тип аргумента - передано: "{0}", ожидалось: '
                            '"efsw.conversion.converter.args.Output".'.format(type(out_obj)))
        self._outputs.append(out_obj if out_obj is not None else Output())
        return self

    @property
    def outputs(self):
        return copy.deepcopy(self._outputs)

    def build(self, io_path_conf, override_defaults=False):
        if not self._inputs:
            raise ConvArgsException('Не задано ни одного входа.')
        if not self._outputs:
            raise ConvArgsException('Не задано ни одного выхода.')
        if not isinstance(io_path_conf, IOPathConfiguration):
            raise TypeError('Аргумент io_path_conf должен быть экземпляром класса IOPathConfiguration.')
        if self._options is None:
            args = self.DEFAULT_CONVERT_ARGS
        elif self._options is not None and not override_defaults:
            args = self.DEFAULT_CONVERT_ARGS + _build_options(self._options)
        else:
            args = _build_options(self._options)
        in_paths, out_paths = io_path_conf.build()
        if len(in_paths) != len(self._inputs):
            raise ConvArgsException('Количество элементов аргумента in_paths ({0}) не совпадает с количеством входов '
                                    '({1}).'.format(len(in_paths), len(self._inputs)))
        for k, i in enumerate(self._inputs):
            args.extend(i.build(in_paths[k]))
        if len(out_paths) != len(self._outputs):
            raise ConvArgsException('Количество элементов аргумента out_paths ({0}) не совпадает с количеством выходов '
                                    '({1}).'.format(len(out_paths), len(self._outputs)))
        for k, o in enumerate(self._outputs):
            args.extend(o.build(out_paths[k]))
        return args


class IOPathConfiguration:

    def __init__(self, in_paths=None, out_paths=None):

        def _check_item_type(i):
            if type(i) != str and not isinstance(i, AbstractIOPathProvider):
                raise TypeError('Все элементы, входящие в аргументы in_paths и out_paths должны быть либо '
                                'строками, указывающими конкретный путь в файловой системе, или экземпляром класса '
                                'AbstractIOPathProvider.')
            return i

        self._inputs = [] if in_paths is None else list(map(_check_item_type, in_paths))
        self._outputs = [] if out_paths is None else list(map(_check_item_type, out_paths))

    def __str__(self):
        return '{0}\r\n{1}'.format(
            '\r\n'.join(['<input{0}> {1}'.format(k, v) for k, v in enumerate(self._inputs)]),
            '\r\n'.join(['<output{0}> {1}'.format(k, v) for k, v in enumerate(self._outputs)])
        )

    def add_input_path(self, in_obj):
        if type(in_obj) != str and not isinstance(in_obj, AbstractIOPathProvider):
            raise TypeError('Аргумент in_obj должен быть либо строкой, либо экземпляром потомка класса '
                            'AbstractIOPathProvider.')
        self._inputs.append(in_obj)
        return self

    @property
    def input_paths(self):
        return copy.deepcopy(self._inputs)

    def add_output_path(self, out_obj):
        if type(out_obj) != str and not isinstance(out_obj, AbstractIOPathProvider):
            raise TypeError('Аргумент in_obj должен быть либо строкой, либо экземпляром потомка класса '
                            'AbstractIOPathProvider.')
        self._outputs.append(out_obj)
        return self

    @property
    def output_paths(self):
        return copy.deepcopy(self._outputs)

    def build(self):

        def _process_item(i):
            if type(i) == str:
                return i
            else:
                path = i.build()
                if not path:
                    raise IOPathResolveException('Невозможно определить путь для {0}.'.format(i))
                return path

        return (
            list(map(_process_item, self._inputs)),
            list(map(_process_item, self._outputs))
        )


class AbstractIOPathProvider:

    def build(self):
        raise NotImplementedError


class InputOutputAbstract(OptionsHandler):

    def __init__(self, options=None, comment=None, allowed_ext=None):
        super().__init__(options)
        self.comment = comment
        self.allowed_ext = allowed_ext if allowed_ext is not None else []

    def build(self, path):
        raise NotImplementedError

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

    # Методы, повторяющие опции ffmpeg в алфавитном порядке

    def c(self, codec_str, stream_id=None):
        if stream_id is not None and not self._check_stream_id(stream_id):
            raise ValueError('Неправильный формат идентификатора потока.')
        return self.set_option_value(
            '-c' if stream_id is None else '-c:{0}'.format(stream_id),
            codec_str
        )

    def codec(self, *args, **kwargs):
        return self.c(*args, **kwargs)

    def f(self, format_str):
        return self.set_option_value('-f', format_str)

    def ss(self, position):
        if re.match(r'^(?:\d{2,}:)?[0-5][0-9]:[0-5][0-9](?:\.\d+)?$', position) is None \
                and re.match(r'^\d+(?:\.\d+)?$', position) is None:
            raise ValueError('Позиция в потоке должна быть указана в формате "[HH:]MM:SS[.mmm]" или "S+[.mmm]".')
        return self.set_option_value('-ss', position)

    def t(self, duration):
        if re.match(r'^(?:\d{2,}:)?[0-5][0-9]:[0-5][0-9](?:\.\d+)?$', duration) is None \
                and re.match(r'^\d+(?:\.\d+)?$', duration) is None:
            raise ValueError('Длительность потока должна быть указана в формате "[HH:]MM:SS[.mmm]" или "S+[.mmm]".')
        return self.set_option_value('-t', duration)


class Input(InputOutputAbstract):

    def build(self, path):
        return _build_options(self._options) + ['-i', path]

    # Методы, повторяющие опции ffmpeg в алфавитном порядке

    def itsoffset(self, offset):
        if re.match(r'^-?(?:\d{2}:)?[0-5][0-9]:[0-5][0-9](?:\.\d+)?$', offset) is None \
                and re.match(r'^-?\d+(?:\.\d+)?$', offset) is None:
            raise ValueError('Смещение должно быть указано в формате "[-][HH:]MM:SS[.mmm]" или "[-]S+[.mmm]".')
        return self.set_option_value('-itsoffset', offset)


class Output(InputOutputAbstract):

    def build(self, path):
        return _build_options(self._options) + [path]

    # Методы, повторяющие опции ffmpeg в алфавитном порядке
