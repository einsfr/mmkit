

class StorageRootNotFound(FileNotFoundError):
    """ Не найдена корневая папка хранилищ """
    pass


class UnknownStorageType(ValueError):
    """
    Запускается, если из базы данных возвращается харнилище с неизвестным типом
    """
    pass