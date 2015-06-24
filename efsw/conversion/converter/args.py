

class ArgumentsBuilder:

    def __init__(self):
        self.inputs = []
        self.outputs = []

    def add_input(self, in_obj):
        if not isinstance(in_obj, Input):
            raise TypeError('Неправильный тип аргумента - передано: "{0}", ожидалось: '
                            '"efsw.conversion.converter.args.Input".'.format(type(in_obj)))
        self.inputs.append(in_obj)

    def add_output(self, out_obj):
        if not isinstance(out_obj, Input):
            raise TypeError('Неправильный тип аргумента - передано: "{0}", ожидалось: '
                            '"efsw.conversion.converter.args.Output".'.format(type(out_obj)))
        self.inputs.append(out_obj)

    def build(self):
        pass


class Input:

    def __init__(self, input_path):
        pass


class Output:

    def __init__(self, output_path):
        pass
