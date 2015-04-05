from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required

from efsw.schedule import views


urlpatterns = patterns(
    '',
    # lineups/ Список сеток вещания
#    url(
#        r'^lineups/$',
#        views.lineup_list,
#        name='lineup_list'
#    ),
#    # lineups/page/2/ Список сеток вещания - постранично
#    url(
#        r'^lineups/page/(?P<page>\d+)/$',
#        views.lineup_list,
#        name='lineup_list_page'
#    ),
    # lineups/current/ Текущая сетка вещания
    url(
        r'^lineups/current/$',
        views.lineup_current,
        name='lineup_current'
    ),
)
