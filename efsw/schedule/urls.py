from django.conf.urls import include, url
from django.contrib.auth.decorators import permission_required

from efsw.schedule import views


# ------------------------- Lineup -------------------------
lineup_patterns = [
    # lineups/list/ Список сеток вещания
    # ( Список сеток вещания )
    url(
        r'^list/$',
        views.lineup_list,
        name='list'
    ),
    # lineups/new/part/modal/ Модальное окно для создания новой сетки вещания
    # ( - )
    url(
        r'^new/part/modal/$',
        views.lineup_new_part_modal,
        name='new_part_modal'
    ),
    # lineups/create/ Создать сетку вещания (POST, действие)
    # ( - )
    url(
        r'^create/$',
        views.lineup_create,
        name='create'
    ),
    # lineups/list/page/2/ Список сеток вещания - постранично
    # ( Список сеток вещания, страница 2 )
    url(
        r'^list/page/(?P<page>\d+)/$',
        views.lineup_list,
        name='list_page'
    ),
    # lineups/show/current/ Текущая сетка вещания для первого по сортировке канала
    # ( Текущая сетка вещания )
    url(
        r'^show/current/$',
        views.lineup_show_current,
        name='show_current'
    ),
    # lineups/show/current/channel/2/ Текущая сетка вещания для канала 2
    # ( Текущая сетка вещания )
    url(
        r'^show/current/channel/(?P<channel_id>\d+)/$',
        views.lineup_show_current,
        name='show_current_channel'
    ),
    # lineups/1/...
    url(
        r'^(?P<lineup_id>\d+)/',
        include([
            # lineups/1/show/ Просмотр сетки вещания
            # ( Просмотр сетки вещания )
            url(
                r'^show/$',
                views.lineup_show,
                name='show'
            ),
            # lineups/1/edit/ Редактирование сетки вещания
            # ( Редактирование сетки вещания )
            url(
                r'^edit/$',
                views.lineup_edit,
                name='edit'
            ),
            # lineups/1/show/part/pp_table_body/ Часть страницы с таблицей фрагментов
            # ( - )
            url(
                r'^show/part/pp_table_body/$',
                views.lineup_show_part_pp_table_body,
                name='show_part_pp_table_body'
            )
        ])
    ),
    # ------------------------- JSON -------------------------
    # lineups/copy/json/?id=1
    # ( - )
    url(
        r'copy/json/',
        views.lineup_copy_json,
        name='copy_json'
    ),
]

# ------------------------- Program -------------------------
program_patterns = [
    # programs/list/ Список программ
    # ( Список программ )
    url(
        r'^list/$',
        views.program_list,
        name='list'
    ),
    # programs/list/page/2/ Список программ - постранично
    # ( Список программ, страница 2 )
    url(
        r'^list/page/(?P<page>\d+)/$',
        views.program_list,
        name='list_page'
    ),
    # programs/new/ Добавление новой программы - форма (GET)
    # ( Добавление новой программы )
    url(
        r'^new/$',
        permission_required('schedule.add_program')(views.program_new),
        name='new'
    ),
    # programs/create/ Добавление новой программы - действие (POST)
    # ( - )
    url(
        r'^create/$',
        permission_required('schedule.add_program')(views.program_create),
        name='create'
    ),
    # programs/5/...
    url(
        r'^(?P<program_id>\d+)/',
        include([
            # programs/5/show/ Описание программы
            # ( Описание программы )
            url(
                r'^show/$',
                views.program_show,
                name='show'
            ),
        ])
    ),
    # ------------------------- JSON -------------------------
    # programs/show/json/?id=5
    # ( - )
    url(
        r'^show/json/',
        views.program_show_json,
        name='show_json'
    )
]

# ------------------------- ProgramPosition -------------------------
pp_patterns = [
    # pps/show/part/modal/
    # ( - )
    url(
        r'^show/part/modal/',
        views.pp_show_part_modal,
        name='show_part_modal'
    ),
    # pps/show/json/?id=12
    # ( - )
    url(
        r'^show/json/',
        views.pp_show_json,
        name='show_json'
    ),
    # pps/edit/part/modal/
    # ( - )
    url(
        r'^edit/part/modal/',
        views.pp_edit_part_modal,
        name='edit_part_modal'
    ),
    # pps/edit/json/?id=12
    # ( - )
    url(
        r'^edit/json/',
        views.pp_edit_json,
        name='edit_json'
    ),
    # pps/delete/json/?id=5
    # ( - )
    url(
        r'delete/json/',
        views.pp_delete_json,
        name='delete_json'
    ),
    # pps/update/json/?id=5
    # ( - )
    url(
        r'update/json/',
        views.pp_update_json,
        name='update_json'
    )
]

urlpatterns = [
    # lineups/...
    url(r'^lineups/', include((lineup_patterns, 'lineup', 'lineup'))),
    # programs/...
    url(r'^programs/', include((program_patterns, 'program', 'program'))),
    # pps/...
    url(r'^pps/', include((pp_patterns, 'pp', 'pp'))),
]