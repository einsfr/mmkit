from django.conf.urls import patterns, url

from efsw.common.auth import views

urlpatterns = patterns(
    '',
    url(
        r'^login/$',
        views.login,
        name='login'
    ),
    url(
        r'^logout/$',
        views.logout,
        name='logout'
    ),
)
