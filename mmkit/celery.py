from __future__ import absolute_import

from celery import Celery

from mmkit.conf import common

app = Celery('mmkit')

app.config_from_object('celeryconfig')
app.autodiscover_tasks(lambda: common.INSTALLED_APPS)
