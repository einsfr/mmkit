from django.db import models


class BaseExtraFieldsMapper():  # TODO: mapping должен стать объектом, а не словарём

    def __init__(self):
        self.mapping = {}

    def get_mapping(self):
        return self.mapping

    def field_exists(self, field_name):
        return field_name in self.get_mapping()

    def add(self, name, field_obj):
        if not type(name) == str:
            raise TypeError('Имя дополнительного поля должно быть строкой.')
        if not isinstance(field_obj, models.Field):
            raise TypeError('Параметр field_obj должен быть подклассов класса django.db.models.Field.')
        field_obj.null = True
        field_obj.set_attributes_from_name(name)
        self.mapping[name] = field_obj
        return self