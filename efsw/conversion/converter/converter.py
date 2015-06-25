import subprocess
from collections import deque

from efsw.conversion.utils import time_conv
from efsw.conversion.converter.exceptions import ConvException, ConvConfException, ConvOutputFormatException

class Converter:

    MAX_LOG_LENGTH = 5

    def __init__(self, settings_object=None):
        if settings_object is None:
            try:
                from django.conf import settings
                settings_object = settings
            except ImportError:
                raise ConvConfException('При использовании класса Converter без Django необходимо передавать '
                                        'конструктору аргумент settings_object, который содержит все настройки, '
                                        'относящиеся к этому экземпляру класса.')
        self.ffmpeg_bin = getattr(settings_object, 'EFSW_FFMPEG_BIN')
        if self.ffmpeg_bin is None:
            raise ConvConfException('В конфигурации не найден путь к исполняемому файлу ffmpeg (EFSW_FFMPEG_BIN).')
        debug = getattr(settings_object, 'DEBUG')
        self.debug = False if debug is None else debug

    def convert(self, args_seq=None, progress_callback=None, success_callback=None, error_callback=None,
                defaults_replace=None):
        if self.debug:
            print('Инициализация процесса кодирования...')
        duration = None
        conv_exception = None
        default_args = [self.ffmpeg_bin]
        default_args.extend(['-hide_banner', '-n', '-nostdin'] if defaults_replace is None else defaults_replace)
        if args_seq is None:
            args = default_args
        else:
            args = default_args + args_seq
        if self.debug:
            args_debug = []
            for a in args:
                if a.find(' ') > 0:
                    args_debug.append('"{0}"'.format(a))
                else:
                    args_debug.append(a)
            print('Запуск: {0}'.format(' '.join(args_debug)))
        log = deque(maxlen=self.MAX_LOG_LENGTH)
        proc = subprocess.Popen(args, stderr=subprocess.PIPE, universal_newlines=True)
        try:
            for line in proc.stderr:
                log.append(line)
                if duration is None:
                    p = line.find('Duration: ')
                    if p >= 0:
                        try:
                            duration = time_conv.time_str_to_seconds(line[p + 10:p + 21])
                        except ValueError as e:
                            raise ConvOutputFormatException(
                                'невозможно определить длительность файла - возможно, изменился формат вывода.'
                            ) from e
                        if duration == 0:
                            raise ConvOutputFormatException(
                                'длительность не может быть равна 0.'
                            )
                else:
                    if line[0:6] == 'frame=':
                        p = line.find('time=')
                        time = line[p + 5:p + 16]
                        try:
                            progress = time_conv.time_str_to_seconds(time) / duration
                        except ValueError as e:
                            raise ConvOutputFormatException(
                                'невозможно определить текущее место кодирования - возможно, изменился формат вывода.'
                            ) from e
                        if self.debug:
                            print('Выполнено: {0:.2%}'.format(progress))
                        if progress_callback is not None:
                            progress_callback(progress)
        except ConvException as e:
            proc.terminate()
            conv_exception = e
        except:
            proc.terminate()
            raise
        finally:
            proc.wait()
            return_code = proc.returncode
            if return_code != 0:
                if self.debug:
                    if conv_exception is not None:
                        print('Ошибка конвертирования: {0}'.format(conv_exception))
                        print('Причина: {0}'.format(conv_exception.__cause__))
                    print('Завершено с ошибкой ({0}). Последние сообщения:'.format(return_code))
                    for l in log:
                        print(l)
                if error_callback is not None:
                    error_callback(log, conv_exception)
            else:
                if self.debug:
                    print('Завершено без ошибок ({0}).'.format(return_code))
                if success_callback is not None:
                    success_callback()
