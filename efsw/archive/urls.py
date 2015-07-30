from django.conf.urls import url, include
from django.contrib.auth.decorators import permission_required

from efsw.archive import views


# ------------------------- Item -------------------------
item_patterns = [
    # items/list/ Основной список элементов
    # Тесты: url sec
    url(
        r'^list/$',
        views.item_list,
        name='list'
    ),
    # items/list/page/2/ Основной список элементов постранично
    # Тесты: url sec
    url(
        r'^list/page/(?P<page>\d+)/$',
        views.item_list,
        name='list_page'
    ),
    # items/new/ Добавление нового элемента - страница с формой (GET)
    # Тесты: url sec
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
            # Тесты: url sec
            url(
                r'^show/$',
                views.item_show,
                name='show'
            ),
            # items/12/show/properties/ Описание одного элемента (свойства)
            # Тесты: url sec
            url(
                r'^show/properties/$',
                views.item_show_properties,
                name='show_properties'
            ),
            # items/12/show/locations/ Описание одного элемента (расположение)
            # Тесты: url sec
            url(
                r'^show/locations/$',
                views.item_show_locations,
                name='show_locations'
            ),
            # items/12/show/links/ Описание одного элемента (связи с другими)
            # Тесты: url sec
            url(
                r'^show/links/$',
                views.item_show_links,
                name='show_links'
            ),
            # items/12/show/log/ Описание одного элемента (журнал)
            # Тесты: url sec
            url(
                r'^show/log/$',
                views.item_show_log,
                name='show_log'
            ),
            # items/12/edit/ Редактирование существующего элемента (GET)
            # Тесты: url sec
            url(
                r'^edit/$',
                permission_required('archive.change_item')(views.item_edit),
                name='edit'
            ),
            # items/12/edit/properties/ Редактирование существующего элемента - свойства (GET)
            # Тесты: url sec
            url(
                r'^edit/properties/$',
                permission_required('archive.change_item')(views.item_edit_properties),
                name='edit_properties'
            ),
            # items/12/edit/locations/ Редактирование существующего элемента - расположение (GET)
            # Тесты: url sec
            url(
                r'^edit/locations/$',
                permission_required('archive.change_item')(views.item_edit_locations),
                name='edit_locations'
            ),
            # items/12/edit/links/ Редактирование существующего элемента - связи (GET)
            # Тесты: url sec
            url(
                r'^edit/links/$',
                permission_required('archive.change_item')(views.item_edit_links),
                name='edit_links'
            ),
        ])
    ),
    # ------------------------- Item JSON -------------------------
    # items/check/links/json/?id=12&type=1&include_id=11 Включаемые элементы - проверка возможности включения (JSON)
    # Тесты: url sec
    url(
        r'^check/links/json/$',
        views.item_check_links_json,
        name='check_links_json'
    ),
    # items/update/links/json/?id=12 Включаемые элементы - обновление (JSON, POST)
    # Тесты: url sec
    url(
        r'^update/links/json/$',
        permission_required('archive.change_item')(views.item_update_links_json),
        name='update_links_json'
    ),
    # items/update/locations/json/?id=12 Положение этого элемента в хранилищах - обновление (JSON, POST)
    # Тесты: url sec
    url(
        r'^update/locations/json/$',
        permission_required('archive.change_itemfilelocation')(views.item_update_locations_json),
        name='update_locations_json'
    ),
    # items/create/json/ Добавление нового элемента - операция с БД (POST)
    # Тесты: url sec
    url(
        r'^create/json/$',
        permission_required('archive.add_item')(views.item_create_json),
        name='create_json'
    ),
    # items/update/properties/json/ Обновление существующего элемента (POST)
    # Тесты: url sec
    url(
        r'^update/properties/json/$',
        permission_required('archive.change_item')(views.item_update_properties_json),
        name='update_properties_json'
    ),
]

# ------------------------- ItemCategory -------------------------
category_patterns = [
    # categories/list/ Список всех категорий
    # Тесты: url sec
    url(
        r'^list/$',
        views.category_list,
        name='list'
    ),
    # categories/list/page/2/ Список всех категорий постранично
    # Тесты: url sec
    url(
        r'^list/page/(?P<page>\d+)/$',
        views.category_list,
        name='list_page'
    ),
    # categories/new/ Добавление категории - форма (GET)
    # Тесты: url sec
    url(
        r'^new/$',
        permission_required('archive.add_itemcategory')(views.category_new),
        name='new'
    ),
    # categories/3/...
    url(
        r'^(?P<category_id>\d+)/',
        include([
            # categories/3/show/items/ Список элементов, входящих в категорию
            # Тесты: url sec
            url(
                r'^show/items/$',
                views.category_show_items,
                name='show_items'
            ),
            # categories/3/show/items/page/2/ Список элементов, входящих в категорию, постранично
            # Тесты: url sec
            url(
                r'^show/items/page/(?P<page>\d+)/$',
                views.category_show_items,
                name='show_items_page'
            ),
            # categories/3/edit/ Редактирование существующей категории - форма (GET)
            # Тесты: url sec
            url(
                r'^edit/$',
                permission_required('archive.change_itemcategory')(views.category_edit),
                name='edit'
            ),
        ])
    ),
    # ------------------------- ItemCategory JSON -------------------------
    # categories/create/json/ Добавление категории - действие (POST)
    # Тесты: url sec
    url(
        r'^create/json/$',
        permission_required('archive.add_itemcategory')(views.category_create_json),
        name='create_json'
    ),
    # categories/update/json/?id=3 Редактирование существующей категории - действие (POST)
    # Тесты: url sec
    url(
        r'^update/json/$',
        permission_required('archive.change_itemcategory')(views.category_update_json),
        name='update_json'
    ),
]

urlpatterns = [
    # search/... Поиск по архиву
    # Тесты: url sec
    url(r'^search/', views.search, name='search'),
    # items/...
    url(r'^items/', include((item_patterns, 'item', 'item'))),
    # categories/...
    url(r'^categories/', include((category_patterns, 'category', 'category'))),
]
