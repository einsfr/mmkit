from django.db import models


class IndexableModel(models.Model):

    def get_index_doc(self):
        raise NotImplementedError('Метод get_index_doc должен быть переопределён моделью перед использованием.')