from django.conf.urls import patterns, url

from efsw.common import tests_views

urlpatterns = patterns(
    '',
    url(
        r'^page/(?P<page>\d+)/$',
        tests_views.empty_view,
        name='page'
    ),
)