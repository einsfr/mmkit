from django.db import models

from efsw.common.search.models import IndexableModel


class IndexableTestModel(IndexableModel, models.Model):

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