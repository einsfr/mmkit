from django.conf.urls import include, url
from django.contrib import admin

from mmkit import views

urlpatterns = [
    url(r'^$', views.home_page),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^archive/', include('efsw.archive.urls', namespace='efsw.archive')),
    url(r'^accounts/', include('efsw.common.accounts.urls', namespace='efsw.common.accounts')),
    url(r'^schedule/', include('efsw.schedule.urls', namespace='efsw.schedule'))
]