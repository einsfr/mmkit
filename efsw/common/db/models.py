from django.db import models
from django.contrib.postgres import fields


class ExtraDataWrapper():

    def __init__(self, extra_data_dict):
        self.__dict__ = extra_data_dict


class ExtraDataField(fields.HStoreField):

    def __init__(self, **kwargs):
        kwargs['null'] = True
        kwargs['blank'] = True
        super().__init__(**kwargs)


class AbstractExtraDataModel(models.Model):

    class Meta:
        abstract = True

    extra_data = ExtraDataField()

    extra_fields_mapper = None

    def save(self, *args, **kwargs):
        if not isinstance(self.extra_data, dict):
            self.extra_data = None
        else:
            field_mapping = self.get_extra_fields_mapping()
            # проверка идёт с учётом всех полей, потому что отсутствующие поля могут быть обязательными
            # но сохраняться будут только те, значение которых не None - нечего тащить лишнее
            cleaned_extra_data = dict()
            for f_name in field_mapping:
                cleaned_value = field_mapping[f_name].clean(self.extra_data.get(f_name, None), None)
                if cleaned_value is not None:
                    cleaned_extra_data[f_name] = cleaned_value
            ed_wrapper = ExtraDataWrapper(cleaned_extra_data)
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
        if isinstance(extra_data, dict):
            cleaned_extra_data = dict([
                (f_name, field_mapping[f_name].clean(extra_data.get(f_name, None), None))
                for f_name in field_mapping
            ])
        else:
            cleaned_extra_data = {}
        loaded_model.extra_data = cleaned_extra_data
        return loaded_model

    @classmethod
    def get_extra_fields_mapper(cls):
        if cls.extra_fields_mapper is None:
            cls.set_extra_fields_mapper()
        return cls.extra_fields_mapper

    @classmethod
    def set_extra_fields_mapper(cls):
        raise NotImplementedError(
            'Метод get_extra_fields_mapper должен быть переопределён моделью перед использованием.'
        )

    @classmethod
    def get_extra_fields_mapping(cls):
        return cls.get_extra_fields_mapper().get_mapping()

    @classmethod
    def extra_field_exists(cls, field_name):
        return cls.get_extra_fields_mapper().field_exists(field_name)