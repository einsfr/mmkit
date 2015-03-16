from django.utils import dateparse

from django.db import models
from django.contrib.postgres import fields


class ExtraDataWrapper():

    def __init__(self, extra_data_dict):
        self.__dict__ = extra_data_dict


class AbstractExtraDataModel(models.Model):

    class Meta:
        abstract = True

    extra_data = fields.HStoreField(
        null=True,
        editable=False
    )

    def save(self, *args, **kwargs):
        if not isinstance(self.extra_data, dict):
            self.extra_data = None
            super().save(*args, **kwargs)
        field_mapping = self.get_extra_fields_mapping()
        cleaned_extra_data = dict([
            (f_name, field_mapping[f_name].clean(f_value, None))
            for f_name, f_value in self.extra_data.items()
            if f_name in field_mapping
        ])
        ed_wrapper = ExtraDataWrapper(self.extra_data)
        prepared_extra_data = dict([
            (f_name, field_mapping[f_name].value_to_string(ed_wrapper))
            for f_name, f_obj in cleaned_extra_data.items()
        ])
        self.extra_data = prepared_extra_data
        super().save(*args, **kwargs)

    @classmethod
    def from_db(cls, db, field_names, values):
        loaded_model = super().from_db(db, field_names, values)
        field_mapping = cls.get_extra_fields_mapping()
        extra_data = values[field_names.index('extra_data')]
        loaded_model.extra_data = dict([
            (f_name, field_mapping[f_name].clean(f_value, None))
            for f_name, f_value in extra_data.items()
            if f_name in field_mapping
        ])
        return loaded_model

    @classmethod
    def get_extra_fields_mapper(cls):
        raise NotImplementedError(
            'Метод get_extra_fields_mapper должен быть переопределён моделью перед использованием.'
        )

    @classmethod
    def get_extra_fields_mapping(cls):
        return cls.get_extra_fields_mapper().get_mapping()

    @classmethod
    def extra_field_exists(cls, field_name):
        return cls.get_extra_fields_mapper().field_exists(field_name)