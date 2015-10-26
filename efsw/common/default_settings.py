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

# Для нужд тестирования стоит отключать этот декоратор, а включать по необходимости
EFSW_IGNORE_REQUIRE_AJAX = False
