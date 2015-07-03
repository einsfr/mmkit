import os

from mmkit.conf.settings import BASE_DIR, APP_ENV

SECRET_KEY = '8j7#!p$kofl+ws9nzomkfwhrd)6_82q0#(kg++$(3py$^+e(t&'

# Подключения к базам данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mmkit',
        'USER': 'mmkit',
        'PASSWORD': 'mmkit',
        'HOST': '127.0.0.1',
    }
}

# Корневая папка хранилища
EFSW_ARCH_STORAGE_ROOT = os.path.join(BASE_DIR, '_storage_{0}'.format(APP_ENV))

# Подключения к Elasticsearch и их опции (http://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch)
# Elasticsearch(EFSW_ELASTIC_HOSTS, **EFSW_ELASTIC_OPTIONS)
EFSW_ELASTIC_HOSTS = [
    {'host': '127.0.0.1'},
]
EFSW_ELASTIC_OPTIONS = {}

BROKER_URL = 'amqp://guest:guest@127.0.0.1:5672/'

EFSW_FFMPEG_BIN = 'E:\\ffmpeg-20150107-git-919e038-win64-static\\bin\\ffmpeg.exe'
