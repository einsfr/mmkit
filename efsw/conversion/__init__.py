from efsw.conversion.converter.exceptions import ConvConfException
from efsw.conversion.converter.converter import Converter

_converters = {}


def get_converter(name='default', settings_object=None):
    global _converters
    if name not in _converters:
        if settings_object is None:
            try:
                from django.conf import settings
                settings_object = settings
            except ImportError:
                raise ConvConfException('При использовании класса Converter без Django необходимо передавать '
                                        'конструктору аргумент settings_object, который содержит все настройки, '
                                        'относящиеся к этому экземпляру класса.')
        _converters[name] = Converter(settings_object)
    return _converters[name]
