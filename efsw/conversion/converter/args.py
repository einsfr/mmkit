from efsw.conversion.converter.exceptions import ConvArgsException

class ArgumentsBuilder:

    def __init__(self):
        self.inputs_list = []
        self.outputs_list = []

    def add_input(self, in_obj):
        if not isinstance(in_obj, Input):
            raise TypeError('Неправильный тип аргумента - передано: "{0}", ожидалось: '
                            '"efsw.conversion.converter.args.Input".'.format(type(in_obj)))
        self.inputs_list.append(in_obj)

    def add_output(self, out_obj):
        if not isinstance(out_obj, Output):
            raise TypeError('Неправильный тип аргумента - передано: "{0}", ожидалось: '
                            '"efsw.conversion.converter.args.Output".'.format(type(out_obj)))
        self.inputs_list.append(out_obj)

    def build(self):
        if not self.inputs_list:
            raise ConvArgsException('Не задано ни одного входа.')
        if not self.outputs_list:
            raise ConvArgsException('Не задано ни одного выхода.')
        args = []
        for i in self.inputs_list:
            args.extend(i.build())
        for o in self.outputs_list:
            args.extend(o.build())
        return args

class Input:

    def __init__(self, path):
        self.path = path

    def build(self):
        return ['-i', self.path]


class Output:

    def __init__(self, path):
        self.path = path

    def build(self):
        return [self.path]
