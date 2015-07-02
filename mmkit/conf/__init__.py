# За идеи спасибо сюда: https://code.djangoproject.com/wiki/SplitSettings
import importlib
import os

CONF_MODULE = __name__
APP_ENV = os.environ.get('APP_ENV', 'dev')

modules = ('common', APP_ENV, 'local', '*{0}_local'.format(APP_ENV))
merge = ('INSTALLED_APPS', 'STATICFILES_DIRS', 'EFSW_ELASTIC_INIT_INDICES', 'CELERY_QUEUES')

def recursive_merge(from_dict, to_dict, root=True):
    for (k, v) in from_dict.items():
        if k in to_dict:
            if isinstance(v, dict) and isinstance(to_dict[k], dict):
                recursive_merge(v, to_dict[k], False)
            elif root and k in merge:
                to_dict[k] = to_dict[k] + v
        else:
            to_dict[k] = v

for module_name in modules:
    if module_name[0] == '*':
        try:
            m = importlib.import_module('{0}.{1}'.format(CONF_MODULE, module_name))
        except ImportError:
            m = None
    else:
        m = importlib.import_module('{0}.{1}'.format(CONF_MODULE, module_name))
    if m is None:
        continue
    m_settings = {}
    for setting in dir(m):
        if setting == setting.upper():
            m_settings[setting] = getattr(m, setting)
    recursive_merge(m_settings, locals())
