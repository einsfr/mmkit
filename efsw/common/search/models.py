

class IndexableModel():

    def get_index_name(self):
        raise NotImplementedError('Метод get_index_name должен быть переопределён моделью перед использованием.')

    def get_doc_type(self):
        raise NotImplementedError('Метод get_doc_type должен быть переопределён моделью перед использованием.')

    def get_doc_body(self):
        raise NotImplementedError('Метод get_doc_body должен быть переопределён моделью перед использованием.')