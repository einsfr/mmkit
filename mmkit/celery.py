from __future__ import absolute_import

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mmkit.conf.settings')
os.environ.setdefault('APP_ENV', 'dev')

from django.conf import settings

app = Celery('mmkit')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
