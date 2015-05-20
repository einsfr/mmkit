import os

# Количество элементов на одной странице списка
EFSW_ARCH_ITEM_LIST_PER_PAGE = 20

# Количество категорий элементов на одной странице списка
EFSW_ARCH_CATEGORY_LIST_PER_PAGE = 20

# Путь к корневой папке для всех хранилищ
EFSW_ARCH_STORAGE_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'storage')

# Если установлено на True - все операции над файловой системой хранилища будут пропускаться
EFSW_ARCH_SKIP_FS_OPS = True

# Режим доступа к создаваемым директориям; может переопределяться параметрами umask
EFSW_ARCH_DIR_MODE = 0o775

# Режим доступа к создаваемым файлам; может переопределяться параметрами umask
EFSW_ARCH_FILE_MODE = 0o664

# Количество записей в логе элемента архива, показываемых сразу на детальной странице
EFSW_ARCH_ITEM_DETAIL_LOG_MESSAGES_COUNT = 3