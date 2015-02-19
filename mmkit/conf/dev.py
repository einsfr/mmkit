from mmkit.conf.common import *

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS += ('debug_toolbar', )

EFSW_ARCH_SKIP_FS_OPS = False

EFSW_ARCH_ITEM_LIST_PER_PAGE = 2

EFSW_ELASTIC_INDEX_PREFIX = 'dev'

from mmkit.conf.dev_local import *