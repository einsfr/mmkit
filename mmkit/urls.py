from django.conf.urls import include, url
from django.contrib import admin

from efsw.home import views

urlpatterns = [
    url(r'^$', views.home_page, name='home'),
    url(r'^accounts/', include('efsw.accounts.urls', namespace='efsw.accounts')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^archive/', include('efsw.archive.urls', namespace='efsw.archive')),
    url(r'^conversion/', include('efsw.conversion.urls', namespace='efsw.conversion')),
    url(r'^im/', include('efsw.im.urls', namespace='efsw.im')),
    url(r'^schedule/', include('efsw.schedule.urls', namespace='efsw.schedule')),
    url(r'^storage/', include('efsw.storage.urls', namespace='efsw.storage')),
]
