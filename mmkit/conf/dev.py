from mmkit.conf.common import *

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS += ('debug_toolbar', )

EFSW_ARCH_SKIP_FS_OPS = False

from mmkit.conf.dev_local import *