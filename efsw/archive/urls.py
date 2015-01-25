from django.conf.urls import patterns, url

from efsw.archive import views


urlpatterns = patterns(
    '',
    # items/
    url(
        r'^items/$',
        views.item_index,
        name='item_index'
    ),
    # items/page/2/
    url(
        r'^items/page/(?P<page>\d+)/$',
        views.item_index,
        name='item_index_page'
    ),
    # items/12/
    url(
        r'^items/(?P<pk>\d+)/$',
        views.ItemDetailView.as_view(),
        name='item_detail'
    ),
    # items/add/
    url(
        r'^items/add/$',
        views.ItemAddView.as_view(),
        name='item_add'
    ),
    # items/12/update/
    url(
        r'^items/(?P<pk>\d+)/update/$',
        views.ItemUpdateView.as_view(),
        name='item_update'
    ),
    # items/12/update/storage/
    url(
        r'^items/(?P<pk>\d+)/update/storage/$',
        views.ItemUpdateStorageView.as_view(),
        name='item_update_storage'
    ),
    # items/12/update/remove-link/17/ @TODO: Это придётся переделать, потому что такой запрос изменяет состояние системы и должен быть POST
    url(
        r'^items/(?P<item_id>\d+)/update/remove-link/(?P<remove_id>\d+)/$',
        views.item_update_remove_link,
        name='item_update_remove_link'
    ),
    # items/12/update/add-link
    url(
        r'^items/(?P<item_id>\d+)/update/add-link$',
        views.item_update_add_link,
        name='item_update_add_link'
    ),
    # categories/
    url(
        r'^categories/$',
        views.CategoryIndexView.as_view(),
        name='category_index'
    ),
    # categories/add/
    url(
        r'^categories/add/$',
        views.CategoryAddView.as_view(),
        name='category_add'
    ),
)
