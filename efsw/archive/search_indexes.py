from haystack import indexes
from efsw.archive import models


class ItemIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    created = indexes.DateField(model_attr='created')

    def get_model(self):
        return models.Item