

class BaseExtraFieldsMapper():

    def __init__(self):
        self.mapping = {}

    def get_mapping(self):
        return self.mapping

    def add(self, name, field_obj):
        self.mapping[name] = field_obj
        return self