import subprocess
import threading

from django.conf import settings


class CliConverter:

    def __init__(self, ffmpeg_bin=None):
        if ffmpeg_bin is None:
            ffmpeg_bin = getattr(settings, 'EFSW_FFMPEG_BIN')
            if ffmpeg_bin is None:
                raise RuntimeError('В конфигурации не найден путь к исполняемому файлу ffmpeg. Установите значение '
                                   'переменной EFSW_FFMPEG_BIN в одном из файлов с настройками или передайте этот '
                                   'путь непосредственно в конструктор с помощью аргумента ffmpeg_bin.')
        self.ffmpeg_bin = ffmpeg_bin
        self.duration = None

    def _calculate_progress(self, current_time):
        if self.duration is None:
            raise  # Нужно написать какую-то исключительную ситуацию

    def convert(self, args_seq=None, progress_callback=None):
        default_args = [self.ffmpeg_bin, '-hide_banner', '-n', '-nostdin']
        if args_seq is None:
            args = default_args
        else:
            args = default_args + args_seq
        proc = subprocess.Popen(args, stderr=subprocess.PIPE, universal_newlines=True)
        for line in proc.stderr:
            if self.duration is None:
                p = line.find('Duration: ')
                if p >= 0:
                    self.duration = line[p + 10:p + 21]  # это нужно преобразовать сразу во что-то, чтоб потом считать
            else:
                if line[0:6] == 'frame=':
                    p = line.find('time=')
                    time = line[p + 5:p + 16]
                    if progress_callback is not None:
                        progress_callback(self._calculate_progress(time))
