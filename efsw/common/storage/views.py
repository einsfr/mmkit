import os

from django import shortcuts
from django.conf import settings
from django.views.decorators import http

from efsw.common import models
from efsw.common.http.response import JsonWithStatusResponse
from efsw.common.storage import utils as storage_utils
from efsw.common.http.decorators import require_ajax


def _get_json_storage_not_found(storage_id):
    return JsonWithStatusResponse.error(
        'Ошибка: хранилище с ID "{0}" не существует.'.format(storage_id),
        'storage_not_found'
    )


def _get_json_path_not_in_storage(path, storage_name):
    return JsonWithStatusResponse.error(
        'Ошибка: путь "{0}" не является частью хранилища "{1}".'.format(path, storage_name),
        'path_not_in_storage'
    )


def _get_json_path_not_exists(path, storage_name):
    return JsonWithStatusResponse.error(
        'Ошибка: путь "{0}" не существует в хранилище "{1}".'.format(path, storage_name),
        'path_not_exists'
    )


def _get_json_path_not_directory(path, storage_name):
    return JsonWithStatusResponse.error(
        'Ошибка: путь "{0}" не указывает на папку в хранилище "{1}".'.format(path, storage_name),
        'path_not_dir'
    )


@require_ajax
@http.require_GET
def nav_ls_json(request):
    storage_id = request.GET.get('s', None)
    try:
        storage = models.FileStorage.objects.get(pk=storage_id)
    except models.FileStorage.DoesNotExist:
        return _get_json_storage_not_found(storage_id)
    path = request.GET.get('p', '')
    dirs_only = request.GET.get('d', False)
    storage_root = storage.get_base_path()
    abs_path = os.path.normpath(os.path.join(storage_root, path))
    if not storage_utils.in_path(storage_root, abs_path) and storage_root != abs_path:
        return _get_json_path_not_in_storage(path, storage.name)
    if not os.path.exists(abs_path):
        return _get_json_path_not_exists(path, storage.name)
    if not os.path.isdir(abs_path):
        return _get_json_path_not_directory(path, storage.name)
    dir_listing = os.listdir(abs_path)
    if not dirs_only:
        return JsonWithStatusResponse.ok(dir_listing)
    else:
        return JsonWithStatusResponse.ok(
            [p for p in dir_listing if os.path.isdir(os.path.join(abs_path, p))]
        )
