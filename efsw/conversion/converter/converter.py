import subprocess
from collections import deque
import re
import os

from efsw.conversion.converter.exceptions import ConvException, ConvConfException, ConvOutputFormatException
from efsw.conversion.converter.args import ArgumentsBuilder, IOPathConfiguration


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
        if not os.path.isfile(self.ffmpeg_bin):
            raise ConvConfException(
                'Исполняемый файл ffmpeg {0} не найден - проверьте правильность указания пути.'.format(self.ffmpeg_bin)
            )
        debug = getattr(settings_object, 'DEBUG')
        self.debug = False if debug is None else debug

    def convert(self, args_builder: ArgumentsBuilder, io_path_conf: IOPathConfiguration, start_callback=None,
                progress_callback=None, success_callback=None, error_callback=None):
        if self.debug:
            print('Инициализация процесса кодирования...')
        args = [self.ffmpeg_bin] + args_builder.build(io_path_conf)
        if self.debug:
            args_debug = []
            for a in args:
                if a.find(' ') > 0:
                    args_debug.append('"{0}"'.format(a))
                else:
                    args_debug.append(a)
            print('Запуск: {0}'.format(' '.join(args_debug)))
        log = deque(maxlen=self.MAX_LOG_LENGTH)
        conv_exception = None
        proc = subprocess.Popen(args, stderr=subprocess.PIPE, universal_newlines=True)
        if start_callback is not None:
            start_callback(proc)
        try:
            for line in proc.stderr:
                log.append(line)
                if line.startswith('frame='):
                    p = line.find('fps=')
                    try:
                        frame = int(line[6:p].strip())
                    except ValueError as e:
                        raise ConvOutputFormatException(
                            'Невозможно определить текущее место кодирования - возможно, изменился формат '
                            'вывода.'
                        ) from e
                    if self.debug:
                        print('Закодировано кадров: {0}'.format(frame))
                    if progress_callback is not None:
                        progress_callback(frame)
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
                    error_callback(return_code, log, conv_exception)
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
