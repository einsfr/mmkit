import os


class AbstractStorage:

    def get_verbose_name(self):
        raise NotImplementedError('Метод get_verbose_name должен быть реализован в дочерних классах.')

    def get_name(self):
        raise NotImplementedError('Метод get_name должен быть реализован в дочерних классах.')

    def get_path(self, element_id):
        raise NotImplementedError('Метод get_path должен быть реализован в дочерних классах.')


class AbstractPublicStorage:

    def get_access_protocols(self):
        raise NotImplementedError('Метод get_access_protocols должен быть реализован в дочерних классах.')

    def get_access_url(self, protocol, element_id):
        raise NotImplementedError('Метод get_access_url должен быть реализован в дочерних классах.')


class AbstractFilesystemStorage(AbstractStorage):

    def __init__(self, name, verbose_name, base_dir):
        self._name = name
        self._verbose_name = verbose_name
        self._base_dir = base_dir

    def get_name(self):
        return self._name

    def get_verbose_name(self):
        return self._verbose_name

    def get_base_dir(self):
        return self._base_dir

    def get_path(self, element_id):
        return os.path.join(self._base_dir, self._get_relative_path(element_id))

    def _get_relative_path(self, element_id):
        raise NotImplementedError('Метод _get_relative_path должен быть реализован в дочерних классах.')

    def is_read_only(self):
        raise NotImplementedError('Метод is_read_only должен быть реализован в дочерних классах.')
