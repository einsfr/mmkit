from django.db import models
from django.contrib.postgres import fields


class ExtraDataWrapper():
    def __init__(self, extra_data_dict):
        if not isinstance(extra_data_dict, dict):
            raise TypeError('Параметр extra_data_dict должен быть словарём.')
        self.__dict__ = extra_data_dict


class AbstractExtraDataModel(models.Model):
    """
    Общий смысл получается примерно такой: extra_data хранит значения дополнительных полей данных и работает как обычное
    поле модели. Информацию о составе этого поля, а точнее - объект, эту информацию собирающий и предоставляющий,
    можно получить с помощью метода get_extra_fields_mapper, который возвращает объект класса BaseExtraFieldsMapper,
    или его потомка или ещё чего-нибудь подобного. Поскольку это поле помечено как нередактируемое - оно само не будет
    появляться в формах или ещё где-нибудь. Но оно и не будет автоматически проходить валидацию. А значит, нужно будет
    сделать свой базовый класс для форм, работающих с такими моделями. Такой класс будет отвечать за преобразование
    отдельных полей в составное поле extra_data и за их отображение в виде виджетов формы. Ну и, конечно, за валидацию
    каждого отдельного поля, т.к. они все являются стандартными Django-полями - проблем с этим быть не должно вообще
    никаких.
    """

    class Meta:
        abstract = True

    extra_data = fields.HStoreField(
        null=True,
        editable=False
    )

    def save(self, *args, **kwargs):
        # Если поле не определено mapper'ом - его при сохранении надо просто выкинуть, а валидации не будет всё равно
        try:
            ed_wrapper = ExtraDataWrapper(self.extra_data)
        except TypeError:
            self.extra_data = None
            super().save(*args, **kwargs)
        cleaned_extra_data = {}
        field_mapping = self.get_extra_fields_mapping()
        for f_name, f_obj in self.extra_data.items():
            if f_name in field_mapping:
                cleaned_extra_data[f_name] = field_mapping[f_name].value_to_string(ed_wrapper)
        self.extra_data = cleaned_extra_data
        super().save(*args, **kwargs)

    def get_extra_fields_mapper(self):
        raise NotImplementedError(
            'Метод get_extra_fields_mapper должен быть переопределён моделью перед использованием.'
        )

    def get_extra_fields_mapping(self):
        return self.get_extra_fields_mapper().get_mapping()

    def extra_field_exists(self, field_name):
        return self.get_extra_fields_mapper().field_exists(field_name)