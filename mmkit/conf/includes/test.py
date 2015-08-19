DEBUG = True

ALLOWED_HOSTS = []

EFSW_ARCH_SKIP_FS_OPS = True  # Не надо это трогать, иначе некоторые тесты могут не проходить. Где необходимо - этот параметр изменён прямо на месте

EFSW_ELASTIC_DISABLE = True  # ES !!!ДЛЯ ТЕСТИРОВАНИЯ!!! надо включать только в тех местах, где тестируется именно он, иначе - начинаются проблемы

EFSW_ELASTIC_CHECK_INTERVAL = -1

EFSW_ELASTIC_ERROR_CHECK_INTERVAL = 0

EFSW_ELASTIC_INDEX_PREFIX = 'test'

EFSW_IGNORE_REQUIRE_AJAX = True
