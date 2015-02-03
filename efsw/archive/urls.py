from django.conf.urls import patterns, url

from efsw.archive import views


urlpatterns = patterns(
    '',
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
        r'^items/(?P<pk>\d+)/$',
        views.ItemDetailView.as_view(),
        name='item_detail'
    ),
    # items/add/ Добавление нового элемента
    url(
        r'^items/add/$',
        views.ItemAddView.as_view(),
        name='item_add'
    ),
    # items/12/update/ Редактирование существующего элемента
    url(
        r'^items/(?P<pk>\d+)/update/$',
        views.ItemUpdateView.as_view(),
        name='item_update'
    ),
    # items/12/update/storage/ Редактирование существующего элемента - раздел хранилища
    url(
        r'^items/(?P<pk>\d+)/update/storage/$',
        views.ItemUpdateStorageView.as_view(),
        name='item_update_storage'
    ),
    # items/12/update/remove-link/ Удаление связи между элементами
    url(
        r'^items/(?P<item_id>\d+)/update/remove-link/$',
        views.item_update_remove_link,
        name='item_update_remove_link'
    ),
    # items/12/update/add-link Добавление связи элементу
    url(
        r'^items/(?P<item_id>\d+)/update/add-link/$',
        views.item_update_add_link,
        name='item_update_add_link'
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
        views.CategoryAddView.as_view(),
        name='category_add'
    ),
    # categories/3/update/ Редактирование существующей категории
    url(
        r'^categories/(?P<pk>\d+)/update$',
        views.CategoryUpdateView.as_view(),
        name='category_update'
    ),
)
