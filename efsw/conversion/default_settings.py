from datetime import timedelta

from kombu import Queue
from kombu.common import Broadcast

EFSW_CONVERTER_PROGRESS_NOTIFY_INTERVAL = 10

EFSW_CONVERTER_PROCESS_PROGRESS_RESULT_TIMEOUT = 3

CELERY_QUEUES = (
    Queue('conversion', routing_key='conversion.#'),
    Broadcast('bc_conversion')
)

CELERYBEAT_SCHEDULE = {
    'process_conversion_queue': {
        'task': 'efsw.conversion.tasks.process_conversion_queue',
        'schedule': timedelta(seconds=30)
    }
}
