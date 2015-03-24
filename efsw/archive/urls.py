from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required

from efsw.archive import views


urlpatterns = patterns(
    '',
    # search/page/2/ Поиск по архиву постранично
    url(
        r'^search/page/(?P<page>\d+)/',
        views.search,
        name='search_page'
    ),
    # search/ Поиск по архиву
    url(
        r'^search/',
        views.search,
        name='search'
    ),
    # items/ Основной список элементов
    url(
        r'^items/$',
        views.item_list,
        name='item_list'
    ),
    # items/page/2/ Основной список элементов постранично
    url(
        r'^items/page/(?P<page>\d+)/$',
        views.item_list,
        name='item_list_page'
    ),
    # items/category/3/ Список элементов, входящих в категорию
    url(
        r'^items/category/(?P<category>\d+)/$',
        views.item_list_category,
        name='item_list_category'
    ),
    # items/category/3/page/2 Список элементов, входящих в категорию, постранично
    url(
        r'^items/category/(?P<category>\d+)/page/(?P<page>\d+)/$',
        views.item_list_category,
        name='item_list_category_page'
    ),
    # items/12/ Детальное описаное одного элемента
    url(
        r'^items/(?P<item_id>\d+)/$',
        views.item_detail,
        name='item_detail'
    ),
    # items/12/_includes/get/ Связи с этим элементом - получение (AJAX)
    url(
        r'^items/(?P<item_id>\d+)/includes/_get/$',
        views.item_includes_get,
        name='item_includes_get'
    ),
    # items/12/_includes/post/ Связи с этим элементом - обновление (AJAX)
    url(
        r'^items/(?P<item_id>\d+)/includes/_post/$',
        permission_required('archive.change_item')(views.item_includes_post),
        name='item_includes_post'
    ),
    # items/12/locations/get/ Положение этого элемента в хранилище - получение (AJAX)
    url(
        r'^items/(?P<item_id>\d+)/locations/_get/$',
        views.item_locations_get,
        name='item_locations_get'
    ),
    # items/12/locations/post/ Положение этого элемента в хранилище - изменение (AJAX)
    url(
        r'^items/(?P<item_id>\d+)/locations/_post/$',
        permission_required('archive.change_itemlocation')(views.item_locations_post),
        name='item_locations_post'
    ),
    # items/12/log/ Все сообщения о внесении изменений в элемент
    url(
        r'^items/(?P<item_id>\d+)/log/$',
        views.item_log,
        name='item_log'
    ),
    # items/add/ Добавление нового элемента
    url(
        r'^items/add/$',
        permission_required('archive.add_item')(views.item_add),
        name='item_add'
    ),
    # items/12/update/ Редактирование существующего элемента
    url(
        r'^items/(?P<item_id>\d+)/update/$',
        permission_required('archive.change_item')(views.item_update),
        name='item_update'
    ),
    # categories/ Список категорий
    url(
        r'^categories/$',
        views.CategoryListView.as_view(),
        name='category_list'
    ),
    # categories/add/ Добавление новой категории
    url(
        r'^categories/add/$',
        permission_required('archive.add_itemcategory')(views.CategoryAddView.as_view()),
        name='category_add'
    ),
    # categories/3/update/ Редактирование существующей категории
    url(
        r'^categories/(?P<pk>\d+)/update/$',
        permission_required('archive.change_itemcategory')(views.CategoryUpdateView.as_view()),
        name='category_update'
    ),
    # storages/_get/ Получение информации обо всех хранилищах (AJAX)
    url(
        r'^storages/_get/$',
        views.storage_get,
        name='storage_get'
    ),
)
