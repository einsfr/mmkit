class EsConfigException(Exception):
    pass


class EsIndexExistsException(Exception):

    def __init__(self, index_name):
        msg = 'Ошибка инициализации: индекс {0} существует. Для удаления существующего индекса во время ' \
              'инициализации необходимо использовать ключ --replace.'
        super().__init__(msg.format(index_name))