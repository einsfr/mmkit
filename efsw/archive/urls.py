from django.conf.urls import patterns, url

from efsw.archive import views


urlpatterns = patterns('',
                       # items/
                       url(r'^items/$', views.IndexView.as_view(), name='item_index'),
                       # items/12/
                       url(r'^items/(?P<pk>\d+)/$', views.DetailView.as_view(), name='item_detail'),
                       # items/add/
                       url(r'^items/add/$', views.CreateView.as_view(), name='item_add'),
                       # items/12/update/
                       url(r'^items/(?P<pk>\d+)/update/$', views.UpdateView.as_view(), name='item_update'),
                       # items/12/update/storage/
                       url(r'^items/(?P<pk>\d+)/update/storage/$',
                           views.UpdateStorageView.as_view(),
                           name='item_update_storage'),
                       # items/12/update/links/
                       url(r'^items/(?P<pk>\d+)/update/link/$',
                           views.UpdateLinkView.as_view(),
                           name='item_update_link'),
                       )
