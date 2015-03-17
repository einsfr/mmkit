

class StorageRootNotFound(FileNotFoundError):
    """ Не найдена корневая папка хранилищ """
    pass


class StorageTypeMismatch(TypeError):
    """
    Используется метод, лишённый смысла для данного вида хранилища
    """
    pass