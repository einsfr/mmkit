import subprocess
import threading

from django.conf import settings

from efsw.common.datetime import conversion


class CliConverter:

    def __init__(self, ffmpeg_bin=None):
        if ffmpeg_bin is None:
            ffmpeg_bin = getattr(settings, 'EFSW_FFMPEG_BIN')
            if ffmpeg_bin is None:
                raise RuntimeError('В конфигурации не найден путь к исполняемому файлу ffmpeg. Установите значение '
                                   'переменной EFSW_FFMPEG_BIN в одном из файлов с настройками или передайте этот '
                                   'путь непосредственно в конструктор с помощью аргумента ffmpeg_bin.')
        self.ffmpeg_bin = ffmpeg_bin

    def convert(self, args_seq=None, progress_callback=None):
        duration = None
        default_args = [self.ffmpeg_bin, '-hide_banner', '-n', '-nostdin']
        if args_seq is None:
            args = default_args
        else:
            args = default_args + args_seq
        proc = subprocess.Popen(args, stderr=subprocess.PIPE, universal_newlines=True)
        for line in proc.stderr:
            if duration is None:
                p = line.find('Duration: ')
                if p >= 0:
                    duration = conversion.time_str_to_seconds(line[p + 10:p + 21])
            else:
                if line[0:6] == 'frame=':
                    p = line.find('time=')
                    time = line[p + 5:p + 16]
                    if progress_callback is not None:
                        progress_callback(conversion.time_str_to_seconds(time) / duration)
        proc.wait()
        return_code = proc.returncode
