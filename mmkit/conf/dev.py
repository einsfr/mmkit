from mmkit.conf.common import *

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS += ('debug_toolbar', )

EFSW_ARCH_SKIP_FS_OPS = False

EFSW_ARCH_ITEM_LIST_PER_PAGE = 2

EFSW_SCHED_PROGRAM_LIST_PER_PAGE = 2

EFSW_SCHED_LINEUP_LIST_PER_PAGE = 2

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    },
}