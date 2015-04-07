from django.conf.urls import url, include
from django.contrib.auth.decorators import permission_required

from efsw.archive import views


urlpatterns = [
    # search/... Поиск по архиву
    url(
        r'^search/',
        views.search,
        name='search'
    ),
    # items/...
    url(
        r'^items/',
        include([
            # items/ Основной список элементов
            url(
                r'^$',
                views.item_list,
                name='list'
            ),
            # items/page/2/ Основной список элементов постранично
            url(
                r'^page/(?P<page>\d+)/$',
                views.item_list,
                name='list_page'
            ),
            # items/new/ Добавление нового элемента - страница с формой (GET)
            url(
                r'^new/$',
                permission_required('archive.add_item')(views.item_new),
                name='new'
            ),
            # items/create/ Добавление нового элемента - операция с БД (POST)
            url(
                r'^create/$',
                permission_required('archive.add_item')(views.item_create),
                name='create'
            ),
            # items/12/...
            url(
                r'^(?P<item_id>\d+)/',
                include([
                    # items/12/ Описание одного элемента
                    url(
                        r'^$',
                        views.item_show,
                        name='show'
                    ),
                    # items/12/json/ Описание одного элемента (JSON)
                    url(
                        r'^json/$',
                        views.item_show_json,
                        name='show_json'
                    ),
                    # items/12/includes/json/ Включаемые элементы (JSON)
                    url(
                        r'^includes/json/$',
                        views.item_includes_list_json,
                        name='includes_list_json'
                    ),
                    # items/12/includes/update/json/ Включаемые элементы - обновление (JSON)
                    url(
                        r'^includes/update/json/$',
                        permission_required('archive.change_item')(views.item_includes_update_json),
                        name='includes_update_json'
                    ),
                    # items/12/locations/json/ Положение этого элемента в хранилищах (JSON)
                    url(
                        r'^locations/json/$',
                        views.item_locations_list_json,
                        name='locations_list_json'
                    ),
                    # items/12/locations/update/json/ Положение этого элемента в хранилищах - обновление (JSON)
                    url(
                        r'^locations/update/json/$',
                        permission_required('archive.change_itemlocation')(views.item_locations_update_json),
                        name='locations_update_json'
                    ),
                    # items/12/logs/ Сообщения о внесении изменения в элемент
                    url(
                        r'^logs/$',
                        views.item_logs_list,
                        name='logs_list'
                    ),
                    # items/12/edit/ Редактирование существующего элемента - форма (GET)
                    url(
                        r'^edit/$',
                        permission_required('archive.change_item')(views.item_edit),
                        name='edit'
                    ),
                    # items/12/update/ Редактирование существующего элемента - операция с БД (POST)
                    url(
                        r'^update/$',
                        permission_required('archive.change_item')(views.item_update),
                        name='update'
                    ),
                ])
            ),
        ], namespace='item')
    ),
    # categories/
    url(
        r'^categories/',
        include([
            # categories/ Список всех категорий
            url(
                r'^$',
                views.CategoryListView.as_view(),
                name='list'
            ),
            # categories/new/ Добавление новой категории - форма (GET)
            url(
                r'^new/$',
                permission_required('archive.add_itemcategory')(views.category_new),
                name='new'
            ),
            # categories/create/ Добавление новой категории - действие (POST)
            url(
                r'^create/$',
                permission_required('archive.add_itemcategory')(views.category_create),
                name='create'
            ),
            # categories/3/...
            url(
                r'^(?P<category_id>\d+)/',
                include([
                    # categories/3/items/ Список элементов, входящих в категорию
                    url(
                        r'items/$',
                        views.category_items_list,
                        name='items_list'
                    ),
                    # categories/3/items/page/2/ Список элементов, входящих в категорию, постранично
                    url(
                        r'^items/page/(?P<page>\d+)/$',
                        views.category_items_list,
                        name='items_list_page'
                    ),
                    # categories/3/edit/ Редактирование существующей категории - форма (GET)
                    url(
                        r'^edit/$',
                        permission_required('archive.change_itemcategory')(views.category_edit),
                        name='edit'
                    ),
                    # categories/3/update/ Редактирование существующей категории - действие (POST)
                    url(
                        r'^update/$',
                        permission_required('archive.change_itemcategory')(views.category_update),
                        name='update'
                    ),
                ])
            ),
        ], namespace='category')
    ),
    # storages/
    url(
        r'^storages/',
        include([
            # storages/json/
            url(
                r'^json/$',
                views.storage_list_json,
                name='storage_list_json'
            ),
        ])
    )
]
