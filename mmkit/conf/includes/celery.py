from kombu import Queue

CELERY_ACCEPT_CONTENT = ['pickle']

CELERY_TASK_SERIALIZER = 'pickle'

CELERY_RESULT_SERIALIZER = 'pickle'

CELERY_TIMEZONE = 'Europe/Moscow'

CELERY_DEFAULT_QUEUE = 'control'

CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'

CELERY_DEFAULT_ROUTING_KEY = 'control.default'

CELERY_DEFAULT_EXCHANGE = 'default'

CELERY_DISABLE_RATE_LIMITS = True  # Если эта возможность не используется, то лучше её отключить - это улучшает производительность

CELERY_QUEUES = (
    Queue('control', routing_key='control.#'),
)

CELERYBEAT_SCHEDULE = {}
