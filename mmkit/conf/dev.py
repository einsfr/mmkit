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

EFSW_ARCH_STORAGE_MOUNT = os.path.join(BASE_DIR, 'dev_storage')

from mmkit.conf.dev_local import *