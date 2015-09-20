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
    def _is_int(i):
        try:
            int(i)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_float(f):
        try:
            float(f)
            return True
        except ValueError:
            return False

    @classmethod
    def _check_stream_id(cls, stream_id):

        if cls._is_int(stream_id):
            return True
        splitted_id = str(stream_id).split(':')
        l = len(splitted_id)
        if l == 1:
            if splitted_id[0] in ['v', 'a', 's', 'd', 't', 'u']:
                return True
            if splitted_id[0][0] == '#' and len(splitted_id[0]) > 1 and cls._is_int(splitted_id[0][1:]):
                return True
            return False
        elif l == 2:
            if splitted_id[0] in ['v', 'a', 's', 'd', 't', 'p', 'i'] and cls._is_int(splitted_id[1]):
                return True
            if splitted_id[0] == 'm':
                return True
        elif l == 3:
            if splitted_id[0] == 'p' and cls._is_int(splitted_id[1]) and cls._is_int(splitted_id[2]):
                return True
            if splitted_id[0] == 'm':
                return True
        return False

    DURATION_POS_ONLY = 0
    DURATION_NEG_ALLOWED = 1
    DURATION_NEG_ONLY = 2

    @classmethod
    def _check_duration_format(cls, duration, neg_mode=None):
        if neg_mode is None:
            neg_mode = cls.DURATION_POS_ONLY
        base_re1 = r'^{0}(?:\d{2,}:)?[0-5][0-9]:[0-5][0-9](?:\.\d+)?$'
        base_re2 = r'^{0}\d+(?:\.\d+)?$'
        if neg_mode == cls.DURATION_POS_ONLY:
            base_re1 = base_re1.format('')
            base_re2 = base_re2.format('')
        elif neg_mode == cls.DURATION_NEG_ALLOWED:
            base_re1 = base_re1.format('-?')
            base_re2 = base_re2.format('-?')
        elif neg_mode == cls.DURATION_NEG_ONLY:
            base_re1 = base_re1.format('-')
            base_re2 = base_re2.format('-')
        return re.match(base_re1, duration) is not None or re.match(base_re2, duration) is not None

    @classmethod
    def _check_size_format(cls, size):
        return re.match(r'^\d+x\d+$', size)

    @classmethod
    def _check_aspect_format(cls, aspect):
        return cls._is_float(aspect) or re.match(r'^\d+:\d+$', aspect) is not None

    def _set_option_value_stream(self, option, value, stream_id=None):
        if stream_id is not None and not self._check_stream_id(stream_id):
            raise ValueError('Wrong stream id: {0}.'.format(stream_id))
        return self.set_option_value(
            option if stream_id is None else '{0}:{1}'.format(option, stream_id),
            value
        )

    # Методы, повторяющие опции ffmpeg в алфавитном порядке

    def ac(self, channels, stream_id=None):
        if not self._is_int(channels):
            raise ValueError('The number of audio channels must be integer, "{0}" provided.'.format(channels))
        return self._set_option_value_stream('-ac', channels, stream_id)

    def ar(self, freq, stream_id=None):
        return self._set_option_value_stream('-ar', freq, stream_id)

    def c(self, codec_str, stream_id=None):
        return self._set_option_value_stream('-c', codec_str, stream_id)

    def f(self, format_str):
        return self.set_option_value('-f', format_str)

    def r(self, fps, stream_id=None):
        return self._set_option_value_stream('-r', fps, stream_id)

    def s(self, size, stream_id=None):
        if not self._check_size_format(size):
            raise ValueError('Wrong size value: {0}. The format "WxH" required.')
        return self._set_option_value_stream('-s', size, stream_id)

    def ss(self, position):
        if not self._check_duration_format(position, self.DURATION_POS_ONLY):
            raise ValueError('Позиция в потоке должна быть указана в формате "[HH:]MM:SS[.mmm]" или "S+[.mmm]".')
        return self.set_option_value('-ss', position)

    def sseof(self, position):
        if not self._check_duration_format(position, self.DURATION_NEG_ONLY) or str(position) != '0':
            raise ValueError('Position must be "0" or must be formatted as "-[HH:]MM:SS[.mmm]" or "-S+[.mmm]".')
        return self.set_option_value('-sseof', position)

    def t(self, duration):
        if not self._check_duration_format(duration):
            raise ValueError('Длительность потока должна быть указана в формате "[HH:]MM:SS[.mmm]" или "S+[.mmm]".')
        return self.set_option_value('-t', duration)


class Input(InputOutputAbstract):

    def build(self, path):
        return _build_options(self._options) + ['-i', path]

    # Методы, повторяющие опции ffmpeg в алфавитном порядке

    def itsoffset(self, offset):
        if self._check_duration_format(offset, self.DURATION_NEG_ALLOWED):
            raise ValueError('Смещение должно быть указано в формате "[-][HH:]MM:SS[.mmm]" или "[-]S+[.mmm]".')
        return self.set_option_value('-itsoffset', offset)


class Output(InputOutputAbstract):

    def build(self, path):
        return _build_options(self._options) + [path]

    # Методы, повторяющие опции ffmpeg в алфавитном порядке

    def an(self):
        return self.set_option('-an')

    def aspect(self, aspect, stream_id=None):
        if not self._check_aspect_format(aspect):
            raise ValueError(
                'Wrong aspect format: {0}. Possible values are floating point number or string "x:y".'.format(aspect)
            )
        return self._set_option_value_stream('-aspect', aspect, stream_id)

    def filter(self, filter_graph, stream_id=None):
        return self._set_option_value_stream('-filter', filter_graph, stream_id)

    def filter_script(self, filename, stream_id=None):
        raise NotImplementedError()

    def frames(self, frame_count, stream_id=None):
        if not self._is_int(frame_count) or int(frame_count) < 0:
            raise ValueError('Frame count must be a positive integer.')
        return self._set_option_value_stream('-frames', frame_count, stream_id)

    def fs(self, limit_size):
        if not self._is_int(limit_size):
            raise ValueError('Size limit must be expressed in bytes.')
        return self.set_option_value('-fs', limit_size)

    def ilme(self):
        return self.set_option('-ilme')

    def metadata(self, meta_dict, meta_specifier=None):
        raise NotImplementedError()

    def pass_num(self, n, stream_id=None):
        if str(n) not in ['1', '2']:
            raise ValueError('Pass number must be 1 or 2, "{0}" provided.'.format(n))
        return self._set_option_value_stream('-pass', n, stream_id)

    def passlogfile(self, prefix, stream_id=None):
        return self._set_option_value_stream('-passlogfile', prefix, stream_id)

    def pre(self, preset_name, stream_id=None):
        return self._set_option_value_stream('-pre', preset_name, stream_id)

    def q(self, q, stream_id=None):
        return self._set_option_value_stream('-q', q, stream_id)

    def rc_override(self, override, stream_id=None):
        raise NotImplementedError()

    def target(self, target_type: str):
        splitted_type = target_type.split('-')
        if len(splitted_type) > 1:
            if splitted_type[0] not in ['pal', 'ntsc', 'film']:
                raise ValueError('Wrong type prefix. Allowed values: "pal-", "ntsc-", "film-".')
            target_prefix = splitted_type[0]
            target_type = splitted_type[1]
        else:
            target_prefix = None
        if target_type not in ['vcd', 'svcd', 'dvd', 'dv', 'dv50']:
            raise ValueError('Wrong type. Allowed values: "vcd", "svcd", "dvd", "dv", "dv50".')
        return self.set_option_value(
            '-target', "{0}-{1}".format(target_prefix, target_type) if target_prefix is not None else target_type
        )

    def top(self, n, stream_id=None):
        if str(n) not in ['-1', '0', '1']:
            raise ValueError('Allowed top values: "-1" - auto, "0" - bottom, "1" - top.')
        return self._set_option_value_stream('-top', n, stream_id)

    def vn(self):
        return self.set_option('-vn')
