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
    # items/12/...
    url(
        r'^(?P<item_id>\d+)/',
        include([
            # items/12/show/ Описание одного элемента
            url(
                r'^show/$',
                views.item_show,
                name='show'
            ),
            # items/12/show/properties/ Описание одного элемента (свойства)
            url(
                r'^show/properties/$',
                views.item_show_properties,
                name='show_properties'
            ),
            # items/12/show/locations/ Описание одного элемента (расположение)
            url(
                r'^show/locations/$',
                views.item_show_locations,
                name='show_locations'
            ),
            # items/12/show/links/ Описание одного элемента (связи с другими)
            url(
                r'^show/links/$',
                views.item_show_links,
                name='show_links'
            ),
            # items/12/show/log/ Описание одного элемента (журнал)
            url(
                r'^show/log/$',
                views.item_show_log,
                name='show_log'
            ),
            # items/12/edit/ Редактирование существующего элемента (GET)
            url(
                r'^edit/$',
                permission_required('archive.change_item')(views.item_edit),
                name='edit'
            ),
            # items/12/edit/properties/ Редактирование существующего элемента - свойства (GET)
            url(
                r'^edit/properties/$',
                permission_required('archive.change_item')(views.item_edit_properties),
                name='edit_properties'
            ),
            # items/12/edit/locations/ Редактирование существующего элемента - расположение (GET)
            url(
                r'^edit/locations/$',
                permission_required('archive.change_item')(views.item_edit_locations),
                name='edit_locations'
            ),
            # items/12/edit/links/ Редактирование существующего элемента - связи (GET)
            url(
                r'^edit/links/$',
                permission_required('archive.change_item')(views.item_edit_links),
                name='edit_links'
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
    # items/create/json/ Добавление нового элемента - операция с БД (POST)
    url(
        r'^create/json/$',
        permission_required('archive.add_item')(views.item_create_json),
        name='create_json'
    ),
    # items/update/properties/json/ Обновление существующего элемента (POST)
    url(
        r'^update/properties/json/',
        permission_required('archive.change_item')(views.item_update_properties_json),
        name='update_properties_json'
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
