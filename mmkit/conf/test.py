from mmkit.conf.common import *

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

EFSW_ARCH_SKIP_FS_OPS = True # Не надо это трогать, иначе некоторые тесты могут не проходить. Где необходимо - этот параметр изменён прямо на месте

from mmkit.conf.test_local import *