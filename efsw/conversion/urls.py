from django.conf.urls import include, url

from efsw.conversion import views

task_patterns = [
    # tasks/list/ Список заданий конвертирования (краткий)
    # Тесты: sec url
    url(
        r'^list/$',
        views.task_list,
        name='list'
    ),
    # tasks/list/finished/ Список заданий конвертирования (завершившиеся)
    # Тесты: sec url
    url(
        r'^list/finished/$',
        views.task_list_finished,
        name='list_finished'
    ),
    # tasks/list/unknown/ Список заданий конвертирования (статус неизвестен)
    # Тесты: sec url
    url(
        r'^list/unknown/$',
        views.task_list_unknown,
        name='list_unknown'
    ),
    # tasks/list/in_progress/ Список заданий конвертирования (в процессе выполнения)
    # Тесты: sec url
    url(
        r'^list/in_progress/$',
        views.task_list_in_progress,
        name='list_in_progress'
    ),
    # tasks/list/enqueued/ Список заданий конвертирования (ожидающие выполнения)
    # Тесты: sec url
    url(
        r'^list/enqueued/$',
        views.task_list_enqueued,
        name='list_enqueued'
    ),
    # tasks/new/
    # Тесты: sec url
    url(
        r'^new/$',
        views.task_new,
        name='new'
    ),
    # tasks/e0593092-fbc5-4b20-99f4-677f8954220f/...
    url(
        r'^(?P<task_id>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/',
        include([
            # tasks/e0593092-fbc5-4b20-99f4-677f8954220f/show/ Описание одного задания
            # Тесты: sec url
            url(
                r'^show/$',
                views.task_show,
                name='show'
            )
        ])
    ),
    # tasks/create/json/
    # Тесты: sec url
    url(
        r'^create/json/$',
        views.task_create_json,
        name='create_json'
    ),
]

profile_patterns = [
    # profiles/list/ Список профилей
    # Тесты: sec url
    url(
        r'^list/$',
        views.profile_list,
        name='list'
    ),
    # profiles/list/page/2/ Список профилей (постранично)
    # Тесты: sec url
    url(
        r'^list/page/(?P<page>\d+)/$',
        views.profile_list,
        name='list_page'
    ),
    # profiles/new/ Создание нового профиля (форма)
    # Тесты: sec url
    url(
        r'^new/$',
        views.profile_new,
        name='new'
    ),
    # profiles/2/...
    url(
        r'^(?P<profile_id>\d+)/',
        include([
            # profiles/2/show/ Описание одного профиля
            # Тесты: sec
            url(
                r'^show/$',
                views.profile_show,
                name='show'
            )
        ])
    ),
    # profiles/show/json/?id=2 Описание одного профиля в формате JSON
    # Тесты: sec url
    url(
        r'^show/json/$',
        views.profile_show_json,
        name='show_json'
    ),
    # profiles/create/json/
    # Тесты: sec url
    url(
        r'^create/json/$',
        views.profile_create_json,
        name='create_json'
    ),
]

urlpatterns = [
    url(r'^tasks/', include((task_patterns, 'task', 'task'))),
    url(r'^profiles/', include((profile_patterns, 'profile', 'profile'))),
]
