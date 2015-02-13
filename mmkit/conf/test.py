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

SECRET_KEY = 'my_very_secret_test_key'

EFSW_ARCH_STORAGE_ROOT = os.path.join(BASE_DIR, '_storage_test')

EFSW_ARCH_SKIP_FS_OPS = True # Не надо это трогать, иначе некоторые тесты могут не проходить. Где необходимо - этот параметр изменён прямо на месте

EFSW_ELASTIC_HOSTS = [
    {'host': '127.0.0.1'},
]

EFSW_ELASTIC_OPTIONS = {}

EFSW_ELASTIC_INIT_MAPPINGS = ()