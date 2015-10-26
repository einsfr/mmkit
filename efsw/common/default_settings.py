import os

from mmkit.conf.settings import BASE_DIR

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'efsw', 'common', 'static'),
]

# Количество соседних страниц, показываемых вокруг текущей
EFSW_COMM_PAGIN_NEIGHBOURS_COUNT = 2

# Текст для ссылки "предыдущая страница"
EFSW_COMM_PAGIN_PREV_TEXT = '«'

# Текст для ссылки "следующая страница"
EFSW_COMM_PAGIN_NEXT_TEXT = '»'

# Интервал ожидания завершения операций ES
EFSW_ELASTIC_TIMEOUT = 5

# Полностью отключает поисковый движок Elasticsearch
EFSW_ELASTIC_DISABLE = False

# Интервал проверки состояния подключения к поисковому движку (в секундах). Значение -1 отключает эту возможность
EFSW_ELASTIC_CHECK_INTERVAL = 60

# Интервал проверки состояния подключения к поисковому движку (в секундах), если предыдущая проверка показала ошибку.
# Значение -1 отключает повторные проверки - сломалось так сломалось
EFSW_ELASTIC_ERROR_CHECK_INTERVAL = 10

# Максимальное количество элементов в результатах поиска
EFSW_ELASTIC_MAX_SEARCH_RESULTS = 50

# Префикс ко всем названиям индексов
EFSW_ELASTIC_INDEX_PREFIX = ''

# Для нужд тестирования стоит отключать этот декоратор, а включать по необходимости
EFSW_IGNORE_REQUIRE_AJAX = False
