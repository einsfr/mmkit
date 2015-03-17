from django.db import models

from efsw.common.search.models import IndexableModel
from efsw.common.db.models import AbstractExtraDataModel
from efsw.common.db.extramap import BaseExtraFieldsMapper


class IndexableTestModel(IndexableModel, models.Model):

    class Meta:
        app_label = 'tests'

    name = models.CharField(
        max_length=255
    )

    created = models.DateField()

    @staticmethod
    def get_doc_type():
        return 'indexabletestmodel'

    @staticmethod
    def get_index_name():
        return 'testmodelindex'

    def get_doc_body(self):
        return {
            'name': self.name,
            'created': self.created.isoformat()
        }


class SourcelessIndexableTestModel(IndexableModel, models.Model):

    class Meta:
        app_label = 'tests'

    name = models.CharField(
        max_length=255
    )

    created = models.DateField()

    @staticmethod
    def get_index_name():
        return 'sourcelessindex'

    @staticmethod
    def get_doc_type():
        return 'sourcelessindexabletestmodel'

    def get_doc_body(self):
        return {
            'name': self.name,
            'created': self.created.isoformat()
        }


class SimpleExtraDataModel(AbstractExtraDataModel):

    class Meta:
        app_label = 'tests'

    @classmethod
    def get_extra_fields_mapper(cls):
        mapper = BaseExtraFieldsMapper()
        mapper.add('ch', models.CharField(
            max_length=32
        ))
        mapper.add('da', models.DateField())
        return mapper


class AllFieldsExtraDataModel(AbstractExtraDataModel):

    class Meta:
        app_label = 'tests'

    @classmethod
    def set_extra_fields_mapper(cls):
        mapper = BaseExtraFieldsMapper()
        mapper.add(
            'bigint',
            models.BigIntegerField()
        ).add(
            'bool',
            models.BooleanField()
        ).add(
            'char',
            models.CharField(max_length=32)
        ).add(
            'date',
            models.DateField()
        ).add(
            'datetime',
            models.DateTimeField()
        ).add(
            'decimal',
            models.DecimalField(max_digits=5, decimal_places=2)
        ).add(
            'email',
            models.EmailField()
        ).add(
            'float',
            models.FloatField()
        ).add(
            'int',
            models.IntegerField()
        ).add(
            'ipaddr',
            models.GenericIPAddressField()
        ).add(
            'nullbool',
            models.NullBooleanField()
        ).add(
            'posint',
            models.PositiveIntegerField()
        ).add(
            'possmint',
            models.PositiveSmallIntegerField()
        ).add(
            'slug',
            models.SlugField()
        ).add(
            'smint',
            models.SmallIntegerField()
        ).add(
            'text',
            models.TextField()
        ).add(
            'time',
            models.TimeField()
        ).add(
            'url',
            models.URLField()
        ).add(
            'uuid',
            models.UUIDField()
        )
        cls.extra_fields_mapper = mapper