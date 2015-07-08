

from efsw.common.storage import AbstractMetaStorage, AbstractPublicStorage, AbstractFilesystemStorage
from efsw.archive import models


class OfflineStorage(AbstractMetaStorage):

    VERBOSE_TYPE = 'Оффлайн'

    def __init__(self, name, verbose_name):
        self._name = name
        self._verbose_name = verbose_name

    def get_verbose_name(self):
        return self._verbose_name

    def get_location(self, element_id):
        return models.ItemLocation.objects.get(storage=self._name, item_id=element_id)

    def get_name(self):
        return self._name


class OnlineMasterStorage(AbstractFilesystemStorage, AbstractPublicStorage):

    VERBOSE_TYPE = 'Онлайн-ведущее'

    def _get_relative_path(self, element_id):
        pass

    def get_access_protocols(self):
        pass

    def is_read_only(self):
        return False

    def get_access_url(self, protocol, element_id):
        pass


class OnlineSlaveStorage(AbstractFilesystemStorage, AbstractPublicStorage):

    VERBOSE_TYPE = 'Онлайн-ведомое'

    def _get_relative_path(self, element_id):
        return models.ItemLocation.objects.get(storage=self._name, item_id=element_id)

    def get_access_protocols(self):
        pass

    def is_read_only(self):
        return True

    def get_access_url(self, protocol, element_id):
        pass

