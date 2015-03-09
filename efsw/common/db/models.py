from django.db import models
from django.contrib.postgres import fields


class AbstractExtraDataModel(models.Model):

    class Meta:
        abstract = True

    extra_data = fields.HStoreField()

    def get_extra_fields_mapper(self):
        raise NotImplementedError(
            'Метод get_extra_fields_mapper должен быть переопределён моделью перед использованием.'
        )