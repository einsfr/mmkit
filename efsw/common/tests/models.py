import json

from django.db import models

from efsw.common.search.models import IndexableModel


class IndexableTestModel(IndexableModel, models.Model):

    name = models.CharField(
        max_length=255
    )

    created = models.DateField()

    def get_doc_type(self):
        return 'indexabletestmodel'

    def get_index_name(self):
        return 'testmodelindex'

    def get_doc_body(self):
        return json.dumps({
            'name': self.name,
            'created': self.created.isoformat()
        })