import subprocess

from celery import shared_task

from efsw.conversion.converter.converter import Converter


@shared_task(queue='conversion')
def convert(args_builder):

    def _start_callback(proc: subprocess.Popen):
        nonlocal process
        process = proc
        print('started')

    def _progress_callback(frame):
        print(frame)

    def _error_callback(log, conv_exception):
        pass

    def _success_callback():
        print('ok')

    process = None
    converter = Converter()
    converter.convert(args_builder, _start_callback, _progress_callback, _success_callback, _error_callback)
