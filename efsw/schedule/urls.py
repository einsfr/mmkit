from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required

from efsw.schedule import views


urlpatterns = patterns(
    '',
    # lineups/ Список сеток вещания
    url(
        r'^lineups/$',
        views.lineup_list,
        name='lineup_list'
    ),
    # lineups/page/2/ Список сеток вещания - постранично
    url(
        r'^lineups/page/(?P<page>\d+)/$',
        views.lineup_list,
        name='lineup_list_page'
    ),
    # lineups/current/ Текущая сетка вещания
    url(
        r'^lineups/current/$',
        views.lineup_current,
        name='lineup_current'
    ),
    # programs/ Список программ
    url(
        r'^programs/$',
        views.program_list,
        name='program_list'
    ),
    # programs/page/2/ Список программ - постранично
    url(
        r'^programs/page/(?P<page>\d+)/$',
        views.program_list,
        name='program_list_page'
    ),
    # programs/add/ Добавление новой программы
    url(
        r'^programs/add/$',
        permission_required('schedule.add_program')(views.program_add),
        name='program_add'
    ),
    # programs/12/ Просмотр деталей программы
    url(
        r'^programs/(?P<program_id>\d+)/$',
        views.program_detail,
        name='program_detail'
    ),
)
