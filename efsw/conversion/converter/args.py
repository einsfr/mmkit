from efsw.conversion.converter.exceptions import ConvArgsException


def _build_options(options):
    result = []
    for o in options:
        if type(o) == tuple:
            result.extend(o)
        else:
            result.append(o)
    return result


class ArgumentsBuilder:

    DEFAULT_CONVERT_ARGS = ['-hide_banner', '-n', '-nostdin']

    def __init__(self):
        self._inputs_list = []
        self._outputs_list = []
        self._global_options = []
        self._override_defaults = False

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

    def set_global_options(self, options, override_defaults=False):
        self._global_options = list(options)
        self._override_defaults = override_defaults

    def build(self):
        if not self._inputs_list:
            raise ConvArgsException('Не задано ни одного входа.')
        if not self._outputs_list:
            raise ConvArgsException('Не задано ни одного выхода.')
        if self._global_options is None:
            args = self.DEFAULT_CONVERT_ARGS
        elif self._global_options is not None and not self._override_defaults:
            args = self.DEFAULT_CONVERT_ARGS + self._global_options
        else:
            args = self._global_options
        for i in self._inputs_list:
            args.extend(i.build())
        for o in self._outputs_list:
            args.extend(o.build())
        return args

    def get_duration_mods(self):
        pass


class InputOutputAbstract:

    def __init__(self, path, options=None):
        if not path:
            raise ValueError('Путь в аргументе path не может быть пустым.')
        self.path = path
        self._options = list(options) if options is not None else []
        # TODO: Нужно проверить опции на предмет ограничений времени???

    def format(self, format_str):
        self._options.append(('-f', format_str))
        return self

    def codec(self, codec_str, stream_id=None):
        self._options.append((
            '-c' if stream_id is None else '-c:{0}'.format(stream_id),
            codec_str
        ))

    def build(self):
        raise NotImplementedError


class Input(InputOutputAbstract):

    def build(self):
        return _build_options(self._options) + ['-i', self.path]


class Output(InputOutputAbstract):

    def build(self):
        return _build_options(self._options) + [self.path]
