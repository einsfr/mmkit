import subprocess, threading

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
        self.progress = 0

    def convert(self, args_seq=None):
        if args_seq is None:
            args = [self.ffmpeg_bin, ]
        else:
            args = args_seq.insert(0, self.ffmpeg_bin)
        proc = subprocess.Popen(args, stderr=subprocess.PIPE)
