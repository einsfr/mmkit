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


class BoolFieldExtraDataModel(AbstractExtraDataModel):

    class Meta:
        app_label = 'tests'

    @classmethod
    def set_extra_fields_mapper(cls):
        mapper = BaseExtraFieldsMapper()
        mapper.add(
            'bool',
            models.BooleanField()
        )
        cls.extra_fields_mapper = mapper


class AllFieldsExtraDataModel(AbstractExtraDataModel):

    class Meta:
        app_label = 'tests'

    @classmethod
    def set_extra_fields_mapper(cls):
        mapper = BaseExtraFieldsMapper()
        mapper.add(
            'bigint',
            models.BigIntegerField(null=True, blank=True)
        ).add(
            'char',
            models.CharField(max_length=32, null=True, blank=True)
        ).add(
            'date',
            models.DateField(null=True, blank=True)
        ).add(
            'datetime',
            models.DateTimeField(null=True, blank=True)
        ).add(
            'decimal',
            models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
        ).add(
            'email',
            models.EmailField(null=True, blank=True)
        ).add(
            'float',
            models.FloatField(null=True, blank=True)
        ).add(
            'int',
            models.IntegerField(null=True, blank=True)
        ).add(
            'ipaddr',
            models.GenericIPAddressField(null=True, blank=True)
        ).add(
            'nullbool',
            models.NullBooleanField(null=True, blank=True)
        ).add(
            'posint',
            models.PositiveIntegerField(null=True, blank=True)
        ).add(
            'possmint',
            models.PositiveSmallIntegerField(null=True, blank=True)
        ).add(
            'slug',
            models.SlugField(null=True, blank=True)
        ).add(
            'smint',
            models.SmallIntegerField(null=True, blank=True)
        ).add(
            'text',
            models.TextField(null=True, blank=True)
        ).add(
            'time',
            models.TimeField(null=True, blank=True)
        ).add(
            'url',
            models.URLField(null=True, blank=True)
        ).add(
            'uuid',
            models.UUIDField(null=True, blank=True)
        )
        cls.extra_fields_mapper = mapper