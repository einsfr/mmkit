from mmkit.conf.common import *

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

INSTALLED_APPS += ('debug_toolbar', )

EFSW_ARCH_STORAGE_ROOT = os.path.join(BASE_DIR, '_storage_dev')

EFSW_ARCH_SKIP_FS_OPS = False

from mmkit.conf.dev_local import *