from efsw.common.storage import errors


class StorageRootNotFound(RuntimeError):
    """ Не найдена корневая папка хранилищ """

    def __init__(self, storage_root, *args, **kwargs):
        super().__init__(errors.STORAGE_ROOT_NOT_FOUND.format(storage_root), *args, **kwargs)


class StorageBaseDirNotFound(RuntimeError):
    """" Не найдена базовая директория хранилища """

    def __init__(self, storage_id, storage_root, *args, **kwargs):
        super().__init__(errors.STORAGE_BASE_DIR_NOT_FOUND.format(storage_id, storage_root), *args, **kwargs)
