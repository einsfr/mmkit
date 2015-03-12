

class BaseExtraFieldsMapper():

    def __init__(self):
        self.mapping = {}

    def get_mapping(self):
        return self.mapping

    def field_exists(self, field_name):
        return field_name in self.get_mapping()

    def add(self, name, field_obj):
        field_obj.null = True
        self.mapping[name] = field_obj
        return self