from django.conf.urls import patterns, include, url
from django.contrib import admin

from mmkit import views

urlpatterns = patterns(
    '',
    url(r'', views.home_page),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^archive/', include('efsw.archive.urls', namespace='efsw.archive'))
)