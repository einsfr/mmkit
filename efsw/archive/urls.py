from django.conf.urls import url, include
from django.contrib.auth.decorators import permission_required

from efsw.archive import views


# ------------------------- Item -------------------------
item_patterns = [
    # items/list/ Основной список элементов
    # ( Список элементов )
    url(
        r'^list/$',
        views.item_list,
        name='list'
    ),
    # items/list/page/2/ Основной список элементов постранично
    # ( Список элементов, страница 2 )
    url(
        r'^list/page/(?P<page>\d+)/$',
        views.item_list,
        name='list_page'
    ),
    # items/new/ Добавление нового элемента - страница с формой (GET)
    # ( Добавление нового элемента )
    url(
        r'^new/$',
        permission_required('archive.add_item')(views.item_new),
        name='new'
    ),
    # items/create/ Добавление нового элемента - операция с БД (POST)
    # ( - )
    url(
        r'^create/$',
        permission_required('archive.add_item')(views.item_create),
        name='create'
    ),
    # items/12/...
    url(
        r'^(?P<item_id>\d+)/',
        include([
            # items/12/show/ Описание одного элемента
            # ( Описание элемента )
            url(
                r'^show/$',
                views.item_show,
                name='show'
            ),
            # items/12/logs/list/ Сообщения о внесении изменения в элемент
            # ( Журнал изменений элемента )
            url(
                r'^logs/list/$',
                views.item_logs_list,
                name='logs_list'
            ),
            # items/12/edit/ Редактирование существующего элемента - форма (GET)
            # ( Редактирование элемента )
            url(
                r'^edit/$',
                permission_required('archive.change_item')(views.item_edit),
                name='edit'
            ),
            # items/12/update/ Редактирование существующего элемента - операция с БД (POST)
            # ( - )
            url(
                r'^update/$',
                permission_required('archive.change_item')(views.item_update),
                name='update'
            ),
        ])
    ),
    # ------------------------- JSON -------------------------
    # items/includes/list/json/?id=12 Включаемые элементы (JSON)
    # ( - )
    url(
        r'^includes/list/json/$',
        views.item_includes_list_json,
        name='includes_list_json'
    ),
    # items/includes/check/json/?id=12&include_id=11 Включаемые элементы - проверка возможности включения (JSON)
    # ( - )
    url(
        r'^includes/check/json/$',
        views.item_includes_check_json,
        name='includes_check_json'
    ),
    # items/includes/update/json/?id=12 Включаемые элементы - обновление (JSON, POST)
    # ( - )
    url(
        r'^includes/update/json/$',
        permission_required('archive.change_item')(views.item_includes_update_json),
        name='includes_update_json'
    ),
    # items/locations/list/json/?id=12 Положение этого элемента в хранилищах (JSON)
    # ( - )
    url(
        r'^locations/list/json/$',
        views.item_locations_list_json,
        name='locations_list_json'
    ),
    # items/locations/update/json/?id=12 Положение этого элемента в хранилищах - обновление (JSON, POST)
    # ( - )
    url(
        r'^locations/update/json/$',
        permission_required('archive.change_itemlocation')(views.item_locations_update_json),
        name='locations_update_json'
    ),
]

# ------------------------- ItemCategory -------------------------
category_patterns = [
    # categories/list/ Список всех категорий
    # ( Список категорий )
    url(
        r'^list/$',
        views.category_list,
        name='list'
    ),
    # categories/list/page/2/ Список всех категорий постранично
    url(
        r'^list/page/(?P<page>\d+)/$',
        views.category_list,
        name='list_page'
    ),
    # categories/new/ Добавление категории - форма (GET)
    # ( Добавление категории )
    url(
        r'^new/$',
        permission_required('archive.add_itemcategory')(views.category_new),
        name='new'
    ),
    # categories/create/ Добавление категории - действие (POST)
    # ( - )
    url(
        r'^create/$',
        permission_required('archive.add_itemcategory')(views.category_create),
        name='create'
    ),
    # categories/3/...
    url(
        r'^(?P<category_id>\d+)/',
        include([
            # categories/3/items/list/ Список элементов, входящих в категорию
            # ( Список элементов в категории )
            url(
                r'items/list/$',
                views.category_items_list,
                name='items_list'
            ),
            # categories/3/items/list/page/2/ Список элементов, входящих в категорию, постранично
            # ( Список элементов в категории, страница 2 )
            url(
                r'^items/list/page/(?P<page>\d+)/$',
                views.category_items_list,
                name='items_list_page'
            ),
            # categories/3/edit/ Редактирование существующей категории - форма (GET)
            # ( Редактирование категории )
            url(
                r'^edit/$',
                permission_required('archive.change_itemcategory')(views.category_edit),
                name='edit'
            ),
            # categories/3/update/ Редактирование существующей категории - действие (POST)
            # ( - )
            url(
                r'^update/$',
                permission_required('archive.change_itemcategory')(views.category_update),
                name='update'
            ),
        ])
    ),
]

# ------------------------- Storage -------------------------
storage_patterns = [
    # ------------------------- JSON -------------------------
    # storages/show/json/?id=12 Описание одного хранилища (JSON)
    # ( - )
    url(
        r'^show/json/$',
        views.storage_show_json,
        name='show_json'
    ),
]

urlpatterns = [
    # search/... Поиск по архиву
    # ( Поиск по архиву )
    url(r'^search/', views.search, name='search'),
    # items/...
    url(r'^items/', include((item_patterns, 'item', 'item'))),
    # categories/...
    url(r'^categories/', include((category_patterns, 'category', 'category'))),
    # storages/
    url(r'^storages/', include((storage_patterns, 'storage', 'storage'))),
]
