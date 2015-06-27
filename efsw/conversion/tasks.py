import time
from threading import Thread

from celery import shared_task
from celery.exceptions import TimeoutError
from django.conf import settings

from efsw.conversion.converter.converter import Converter
from efsw.conversion import default_settings


class ConvertCallbacksFactory:

    def __init__(self, conv_id):
        self.conv_id = conv_id
        self.progress_call_interval = getattr(
            settings,
            'EFSW_CONVERTER_PROGRESS_NOTIFY_INTERVAL',
            default_settings.EFSW_CONVERTER_PROGRESS_NOTIFY_INTERVAL
        )
        self.last_progress_call_ts = 0.0
        self.convert_proc = None
        self.process_result_timeout = getattr(
            settings,
            'EFSW_CONVERTER_PROCESS_PROGRESS_RESULT_TIMEOUT',
            default_settings.EFSW_CONVERTER_PROCESS_PROGRESS_RESULT_TIMEOUT
        )

    def get_start_callback(self):

        def _start_callback(proc):
            self.convert_proc = proc
            notify_conversion_started.delay(self.conv_id)

        return _start_callback

    def get_progress_callback(self):

        def _process_result(result):
            try:
                print(result.wait(timeout=self.process_result_timeout, interval=1))
            except TimeoutError:
                print('timeout')

        def _progress_callback(frame):
            ts = time.time()
            if ts - self.last_progress_call_ts >= self.progress_call_interval:
                self.last_progress_call_ts = ts
                result = notify_conversion_progress.delay(self.conv_id, frame)
                Thread(target=_process_result, name='conv_result_process', args=(result, )).start()

        return _progress_callback

    def get_success_callback(self):

        def _success_callback():
            notify_conversion_success.delay(self.conv_id)

        return _success_callback

    def get_error_callback(self):

        def _error_callback(log, conv_exception):
            error_msg = None
            notify_conversion_error.delay(self.conv_id, error_msg)

        return _error_callback

    def get_callback_dict(self):
        return {
            'start_callback': self.get_start_callback(),
            'progress_callback': self.get_progress_callback(),
            'success_callback': self.get_success_callback(),
            'error_callback': self.get_error_callback()
        }


@shared_task(queue='conversion', ignore_result=True)
def convert(conv_id, args_builder):
    converter = Converter()
    cb_factory = ConvertCallbacksFactory(conv_id)
    converter.convert(args_builder, **cb_factory.get_callback_dict())


@shared_task(queue='control', ignore_result=True)
def notify_conversion_started(conv_id):
    print('conversion started: {0}'.format(conv_id))


@shared_task(queue='control')
def notify_conversion_progress(conv_id, frame):
    print('{0} progress: {1}'.format(conv_id, frame))
    return 'progress received'


@shared_task(queue='control', ignore_result=True)
def notify_conversion_error(conv_id, error_msg):
    print('convertion error: {0}'.format(conv_id))


@shared_task(queue='control', ignore_result=True)
def notify_conversion_success(conv_id):
    print('conversion complete: {0}'.format(conv_id))
