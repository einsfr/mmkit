from datetime import timedelta

from kombu import Queue
from kombu.common import Broadcast
from celery.schedules import crontab

EFSW_CONVERTER_PROGRESS_NOTIFY_INTERVAL = 10

EFSW_CONVERTER_PROCESS_PROGRESS_RESULT_TIMEOUT = 3

EFSW_CONVERTER_MAX_START_WAITING_COUNT = 2

EFSW_CONVERTER_MAX_SUCCESS_LIFETIME = timedelta(weeks=1)

EFSW_CONVERTER_MAX_ERROR_LIFETIME = None

EFSW_CONVERTER_MAX_CANCELED_LIFETIME = timedelta(weeks=1)

CELERY_QUEUES = (
    Queue('conversion', routing_key='conversion.#'),
    Broadcast('bc_conversion')
)

CELERYBEAT_SCHEDULE = {
    'process_conversion_queue': {
        'task': 'efsw.conversion.tasks.process_conversion_queue',
        'schedule': timedelta(seconds=30)
    },
    'reorder_conversion_queue': {
        'task': 'efsw.conversion.tasks.reorder_conversion_queue',
        'schedule': crontab(hour=3, minute=0)
    }
}
