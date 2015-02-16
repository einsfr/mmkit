from mmkit.conf.common import *

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

EFSW_ARCH_SKIP_FS_OPS = True  # Не надо это трогать, иначе некоторые тесты могут не проходить. Где необходимо - этот параметр изменён прямо на месте

EFSW_ELASTIC_DISABLE = True  # ES !!!ДЛЯ ТЕСТИРОВАНИЯ!!! надо включать только в тех местах, где тестируется именно он, иначе - начинаются проблемы

from mmkit.conf.test_local import *