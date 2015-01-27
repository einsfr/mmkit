from django.conf.urls import patterns, url

from efsw.archive import views


urlpatterns = patterns(
    '',
    # items/ Основной индекс элементов
    url(
        r'^items/$',
        views.item_index,
        name='item_index'
    ),
    # items/page/2/ Основной индекс элементов постранично
    url(
        r'^items/page/(?P<page>\d+)/$',
        views.item_index,
        name='item_index_page'
    ),
    # items/category/3/ Индекс элементов, входящих в категорию
    url(
        r'^items/category/(?P<category>\d+)/$',
        views.item_index_category,
        name='item_index_category'
    ),
    # items/category/3/page/2 Индекс элементов, входящих в категорию, постранично
    url(
        r'^items/category/(?P<category>\d+)/page/(?P<page>\d+)/$',
        views.item_index_category,
        name='item_index_category_page'
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
    # items/12/update/remove-link/17/ Удаление связи между элементами 12 (главный) и 17 (включённый)
    # @TODO: Это придётся переделать, потому что такой запрос изменяет состояние системы и должен быть POST
    url(
        r'^items/(?P<item_id>\d+)/update/remove-link/(?P<remove_id>\d+)/$',
        views.item_update_remove_link,
        name='item_update_remove_link'
    ),
    # items/12/update/add-link Добавление связи элементу
    url(
        r'^items/(?P<item_id>\d+)/update/add-link$',
        views.item_update_add_link,
        name='item_update_add_link'
    ),
    # categories/ Индекс категорий
    url(
        r'^categories/$',
        views.CategoryIndexView.as_view(),
        name='category_index'
    ),
    # categories/add/ Добавление новой категории
    url(
        r'^categories/add/$',
        views.CategoryAddView.as_view(),
        name='category_add'
    ),
)
