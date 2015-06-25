import subprocess
from collections import deque
import re

from efsw.conversion.utils import time_conv
from efsw.conversion.converter.exceptions import ConvException, ConvConfException, ConvOutputFormatException

class Converter:

    MAX_LOG_LENGTH = 5
    INFO_CMDS_TIMEOUT = 3

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

    def convert(self, args_seq=None, start_callback=None, progress_callback=None, success_callback=None,
                error_callback=None, defaults_replace=None):
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
        if start_callback is not None:
            start_callback(proc)
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
                                'Невозможно определить длительность файла - возможно, изменился формат вывода.'
                            ) from e
                        if duration == 0 and self.debug:
                            print('Длительность равна нулю - возможно, это "живой" поток?')
                else:
                    if line[0:6] == 'frame=':
                        p = line.find('time=')
                        time = line[p + 5:p + 16]
                        try:
                            time_sec = time_conv.time_str_to_seconds(time)
                        except ValueError as e:
                            raise ConvOutputFormatException(
                                'Невозможно определить текущее место кодирования - возможно, изменился формат '
                                'вывода.'
                            ) from e
                        if duration != 0:
                            progress = time_sec / duration
                            if self.debug:
                                print('Выполнено: {0:.2%}'.format(progress))
                        else:
                            progress = None
                            if self.debug:
                                print('Текущее место кодирования: {0}'.format(time))
                        if progress_callback is not None:
                            progress_callback(time_sec, progress)
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

    def get_version(self):
        output = subprocess.check_output(
            [self.ffmpeg_bin] + ['-version'],
            stderr=subprocess.STDOUT,
            timeout=self.INFO_CMDS_TIMEOUT
        )
        if self.debug:
            print(output.decode())
        output_list = output.split(b'\r\n')
        result = dict()
        if output_list[0][:14] != b'ffmpeg version':
            raise ConvOutputFormatException(
                'Невозможно определить версию ffmpeg - возможно, изменился формат вывода.'
            )
        result['version'] = output_list[0].split(b' ')[2].decode()
        if output_list[2][:13] != b'configuration':
            raise ConvOutputFormatException(
                'Невозможно определить конфигурацию ffmpeg - возможно, изменился формат вывода.'
            )
        conf_list = output_list[2].decode().split(' ')
        result['configuration'] = [i for i in map(lambda x: x[2:], conf_list[1:])]
        libs = dict()
        r = re.compile(r'^(\w+)\s+(\d+)\.\s*(\d+)\.\s*(\d+).*')
        for line in output_list[3:]:
            line_dec = line.decode()
            match = r.match(line_dec)
            if match is not None:
                try:
                    libs[match.group(1)] = (int(match.group(2)), int(match.group(3)), int(match.group(4)))
                except ValueError:
                    raise ConvOutputFormatException(
                        'Невозможно определить версии библиотек - возможно, изменился формат вывода.'
                    )
            else:
                break
        if not libs:
            raise ConvOutputFormatException(
                'Невозможно определить версии библиотек - возможно, изменился формат вывода.'
            )
        result['libraries'] = libs
        return result

    def get_formats(self):
        output = subprocess.check_output(
            [self.ffmpeg_bin] + ['-hide_banner', '-formats'],
            stderr=subprocess.STDOUT,
            timeout=self.INFO_CMDS_TIMEOUT
        )
        if self.debug:
            print(output.decode())
        output_list = output.split(b'\r\n')
        formats = dict()
        r = re.compile(r'^(.{3}) (\S+)\s+')
        for line in output_list[4:]:
            line_dec = line.decode()
            match = r.match(line_dec)
            if match is not None:
                formats[match.group(2)] = (
                    match.group(1)[1] == 'D',
                    match.group(1)[2] == 'E',
                )
            else:
                break
        if not formats:
            raise ConvOutputFormatException(
                'Невозможно определить поддерживаемые форматы - возможно, изменился формат вывода.'
            )
        return formats
