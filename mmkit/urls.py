from django.conf.urls import include, url
from django.contrib import admin

from efsw.common.home import views

urlpatterns = [
    url(r'^$', views.home_page, name='home'),
    url(r'^common/', include('efsw.common.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^archive/', include('efsw.archive.urls', namespace='efsw.archive')),
    url(r'^schedule/', include('efsw.schedule.urls', namespace='efsw.schedule')),
    url(r'^conversion/', include('efsw.conversion.urls', namespace='efsw.conversion'))
]
