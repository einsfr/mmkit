import os

from mmkit.conf.settings import BASE_DIR

SECRET_KEY = 'my-really-secret-production-key-and-i-will-not-show-it-to-anybody'

ALLOWED_HOSTS = [
    'mmkit.example.com',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mmkit',
        'USER': 'mmkit',
        'PASSWORD': 'password',
        'HOST': 'localhost'  # Нужно убрать, если соединение происходит через socket
    }
}

# Корневая папка для монтирования ВСЕХ хранилищ
EFSW_STORAGE_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'storage')

EFSW_ELASTIC_HOSTS = [
    {'host': '127.0.0.1'},
]

EFSW_ELASTIC_OPTIONS = {}

EMAIL_HOST = 'smtp.example.com'

EMAIL_PORT = 25

EMAIL_HOST_PASSWORD = 'mail_password'

EMAIL_HOST_USER = 'mail_user'

EMAIL_USE_SSL = False

EMAIL_USE_TLS = False

STATIC_ROOT = '/path/to/static/files/dir/'

ADMINS = (
    ('admin', 'admin@example.com'),
)

MANAGERS = (
    ('manager', 'manager@example.com'),
)

BROKER_URL = 'amqp://guest:guest@127.0.0.1:5672/'

EFSW_FFMPEG_BIN = '/opt/ffmpeg/bin/ffmpeg'
