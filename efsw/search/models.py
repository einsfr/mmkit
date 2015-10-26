

class IndexableModel:

    @staticmethod
    def get_index_name():
        raise NotImplementedError('Метод get_index_name должен быть переопределён моделью перед использованием.')

    @staticmethod
    def get_doc_type():
        raise NotImplementedError('Метод get_doc_type должен быть переопределён моделью перед использованием.')

    def get_doc_body(self):
        raise NotImplementedError('Метод get_doc_body должен быть переопределён моделью перед использованием.')