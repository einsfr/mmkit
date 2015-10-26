import importlib
import os
import re

CONF_ROOT = str(__name__)[:str(__name__).rfind('.')]

CONF_INCLUDES_DIR = 'includes'

APP_ENV = os.environ.get('APP_ENV', 'dev')

APP_DEFAULT_SETTINGS_MODULE = 'default_settings'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'efsw.archive',
    'efsw.common',
    'efsw.schedule',
    'efsw.conversion',
    'efsw.accounts',
    'efsw.im',
    'efsw.home',
    'efsw.storage',
)

modules = (r'@efsw\.', 'common', 'celery', APP_ENV, 'local')
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
        else:
            to_dict[k] = v

loaded_modules = []

for module_name in modules:
    if not module_name:
        raise ValueError('Имя или иное обозначение модуля не может быть пустым.')
    opt_part = module_name[:2] if len(module_name) > 2 else module_name[:len(module_name) - 1]
    optional = '*' in opt_part
    app_re = '@' in opt_part
    if optional and app_re:
        module_name = module_name[2:]
    elif optional or app_re:
        module_name = module_name[1:]
    if not app_re:
        full_name = '{0}.{1}.{2}'.format(CONF_ROOT, CONF_INCLUDES_DIR, module_name)
        if full_name not in loaded_modules:
            if optional:
                try:
                    m = importlib.import_module(full_name)
                except ImportError:
                    m = None
            else:
                m = importlib.import_module(full_name)
            if m is None:
                continue
            m_settings = {}
            for setting in dir(m):
                if setting.isupper():
                    m_settings[setting] = getattr(m, setting)
            recursive_merge(m_settings, globals())
            loaded_modules.append(full_name)
    else:
        installed_apps = globals().get('INSTALLED_APPS')
        if not installed_apps:
            raise RuntimeError('Использовать @ для загрузки конфигураций из приложений можно только после загрузки '
                               'части конфигурации, содержащей переменную INSTALLED_APPS.')
        r = re.compile(module_name)
        import_list = ['{0}.{1}'.format(app, APP_DEFAULT_SETTINGS_MODULE) for app in installed_apps if r.match(app)]
        if not import_list:
            continue
        for i in import_list:
            if i not in loaded_modules:
                if optional:
                    try:
                        m = importlib.import_module(i)
                    except ImportError:
                        m = None
                else:
                    m = importlib.import_module(i)
                if m is None:
                    continue
                m_settings = {}
                for setting in dir(m):
                    if setting.isupper():
                        m_settings[setting] = getattr(m, setting)
                recursive_merge(m_settings, globals())
                loaded_modules.append(i)
