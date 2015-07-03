import os

from mmkit.conf.settings import BASE_DIR

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'efsw', 'schedule', 'static')
]

# Количество программ на одной странице списка
EFSW_SCHED_PROGRAM_LIST_PER_PAGE = 20

# Количество сеток вещания на одной странице списка
EFSW_SCHED_LINEUP_LIST_PER_PAGE = 10

# Количество каналов на одной странице списка
EFSW_SCHED_CHANNEL_LIST_PER_PAGE = 20
