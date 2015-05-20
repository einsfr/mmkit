from django.conf.urls import include, url
from django.contrib.auth.decorators import permission_required

from efsw.schedule import views


# ------------------------- Lineup -------------------------
lineup_patterns = [
    # lineups/list/ Список сеток вещания
    url(
        r'^list/$',
        views.lineup_list,
        name='list'
    ),
    # lineups/new/ Создание сетки вещания
    url(
        r'^new/$',
        permission_required('schedule.add_lineup')(views.lineup_new),
        name='new'
    ),
    # lineups/list/page/2/ Список сеток вещания - постранично
    url(
        r'^list/page/(?P<page>\d+)/$',
        views.lineup_list,
        name='list_page'
    ),
    # lineups/show/current/ Текущая сетка вещания для первого по сортировке канала
    url(
        r'^show/current/$',
        views.lineup_show_current,
        name='show_current'
    ),
    # lineups/show/current/channel/2/ Текущая сетка вещания для канала 2
    url(
        r'^show/current/channel/(?P<channel_id>\d+)/$',
        views.lineup_show_current,
        name='show_current_channel'
    ),
    # lineups/copy/part/modal/ Содержимое модального окна для копирования сетки вещания
    url(
        r'copy/part/modal/$',
        permission_required('schedule.add_lineup')(views.lineup_copy_part_modal),
        name='copy_part_modal'
    ),
    # lineups/activate/part/modal/ Содержимое модального окна для перевода сетки из разряда черновиков
    url(
        r'activate/part/modal/$',
        permission_required('schedule.change_lineup')(views.lineup_activate_part_modal),
        name='activate_part_modal'
    ),
    # lineups/make_draft/part/modal/ Содержимое модального окна для перевода сетки снова в разряд черновиков
    url(
        r'make_draft/part/modal/$',
        permission_required('schedule.change_lineup')(views.lineup_make_draft_part_modal),
        name='make_draft_part_modal'
    ),
    # lineups/1/...
    url(
        r'^(?P<lineup_id>\d+)/',
        include([
            # lineups/1/show/ Просмотр сетки вещания
            url(
                r'^show/$',
                views.lineup_show,
                name='show'
            ),
            # lineups/1/edit/ Редактирование сетки вещания
            url(
                r'^edit/$',
                permission_required('schedule.change_lineup')(views.lineup_edit),
                name='edit'
            ),
            # lineups/1/edit/structure/ Редактирование (структура)
            url(
                r'^edit/structure/$',
                permission_required('schedule.change_lineup')(views.lineup_edit_structure),
                name='edit_structure'
            ),
            # lineups/1/edit/properties/ Редактирование (свойства)
            url(
                r'^edit/properties/$',
                permission_required('schedule.change_lineup')(views.lineup_edit_properties),
                name='edit_properties'
            ),
            # lineups/1/show/part/pp_table_body/ Часть страницы с таблицей фрагментов
            url(
                r'^show/part/pp_table_body/$',
                views.lineup_show_part_pp_table_body,
                name='show_part_pp_table_body'
            )
        ])
    ),
    # ------------------------- JSON -------------------------
    # lineups/copy/json/?id=1 Копирование сетки вещания, POST
    url(
        r'copy/json/',
        permission_required('schedule.add_lineup')(views.lineup_copy_json),
        name='copy_json'
    ),
    # lineups/activate/json/?id=1 Активация сетки вещания, POST
    url(
        r'activate/json/',
        permission_required('schedule.change_lineup')(views.lineup_activate_json),
        name='activate_json'
    ),
    # lineups/make_draft/json/?id=1 Возврат сетки вещания в состояние черновика
    url(
        r'make_draft/json/',
        permission_required('schedule.change_lineup')(views.lineup_make_draft_json),
        name='make_draft_json'
    ),
    # lineups/create/json/ Создать сетку вещания (POST, действие)
    url(
        r'^create/json/$',
        permission_required('schedule.add_lineup')(views.lineup_create_json),
        name='create_json'
    ),
    # lineups/update/json/?id=2 Обновить сетку вещания (POST, действие)
    url(
        r'^update/json/$',
        permission_required('schedule.change_lineup')(views.lineup_update_json),
        name='update_json'
    ),
]

# ------------------------- Program -------------------------
program_patterns = [
    # programs/list/ Список программ
    url(
        r'^list/$',
        views.program_list,
        name='list'
    ),
    # programs/list/page/2/ Список программ - постранично
    url(
        r'^list/page/(?P<page>\d+)/$',
        views.program_list,
        name='list_page'
    ),
    # programs/new/ Добавление новой программы - форма (GET)
    url(
        r'^new/$',
        permission_required('schedule.add_program')(views.program_new),
        name='new'
    ),
    # programs/5/...
    url(
        r'^(?P<program_id>\d+)/',
        include([
            # programs/5/show/ Описание программы
            url(
                r'^show/$',
                views.program_show,
                name='show'
            ),
        ])
    ),
    # ------------------------- JSON -------------------------
    # programs/show/json/?id=5 Сведения о программе
    url(
        r'^show/json/',
        views.program_show_json,
        name='show_json'
    ),
    # programs/create/json/ Добавление новой программы - действие (POST)
    url(
        r'^create/json/$',
        permission_required('schedule.add_program')(views.program_create_json),
        name='create_json'
    ),
]

# ------------------------- ProgramPosition -------------------------
pp_patterns = [
    # pps/show/part/modal/ Модальное окно для просмотра положения программы в сетке
    url(
        r'^show/part/modal/',
        views.pp_show_part_modal,
        name='show_part_modal'
    ),
    # pps/show/json/?id=12 Сведения о положении программы в сетке
    url(
        r'^show/json/',
        views.pp_show_json,
        name='show_json'
    ),
    # pps/edit/part/modal/ Модальное окно для редактирования положения программы в сетке
    url(
        r'^edit/part/modal/',
        permission_required('schedule.change_programposition')(views.pp_edit_part_modal),
        name='edit_part_modal'
    ),
    # pps/edit/json/?id=12 Редактирование положения программы, POST
    url(
        r'^edit/json/',
        permission_required('schedule.change_programposition')(views.pp_edit_json),
        name='edit_json'
    ),
    # pps/delete/json/?id=5 Удаление положения программы, POST
    url(
        r'delete/json/',
        permission_required('schedule.change_programposition')(views.pp_delete_json),
        name='delete_json'
    ),
    # pps/update/json/?id=5 Обновление положения программы, POST
    url(
        r'update/json/',
        permission_required('schedule.change_programposition')(views.pp_update_json),
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