import os
from datetime import datetime, timedelta

from efsw.conversion.converter.args import AbstractIOPathProvider
from efsw.common.models import FileStorage


class FileStorageIOPathProvider(AbstractIOPathProvider):

    _storage_cache = {}

    STORAGE_CACHE_LIFETIME = timedelta(seconds=30)

    def __init__(self, storage_id, path):
        self.storage_id = str(storage_id)
        self.path = path

    def __str__(self):
        return 'File "{0}" in storage "{1}"'.format(self.path, self.storage_id)

    def build(self):
        if self.storage_id not in type(self)._storage_cache \
                or type(self)._storage_cache[self.storage_id][1] < datetime.now():
            try:
                storage = FileStorage.objects.get(pk=self.storage_id)
            except FileStorage.DoesNotExist:
                return None
            type(self)._storage_cache[self.storage_id] = (storage, datetime.now() + type(self).STORAGE_CACHE_LIFETIME)
        else:
            storage = type(self)._storage_cache[self.storage_id][0]
        return os.path.normpath(os.path.join(storage.get_base_path(), self.path))
