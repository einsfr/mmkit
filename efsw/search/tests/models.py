from django.db import models

from efsw.search.models import IndexableModel


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