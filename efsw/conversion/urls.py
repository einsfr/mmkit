from django.conf.urls import include, url
from django.contrib.auth.decorators import permission_required

from efsw.conversion import views

task_patterns = [
    # tasks/list/ Список заданий конвертирования (краткий)
    # Тесты:
    url(
        r'^list/$',
        views.task_list,
        name='list'
    ),
    # tasks/list/finished/ Список заданий конвертирования (завершившиеся)
    # Тесты:
    url(
        r'^list/finished/$',
        views.task_list_finished,
        name='list_finished'
    ),
    # tasks/list/unknown/ Список заданий конвертирования (статус неизвестен)
    # Тесты:
    url(
        r'^list/unknown/$',
        views.task_list_unknown,
        name='list_unknown'
    ),
    # tasks/list/in_progress/ Список заданий конвертирования (в процессе выполнения)
    # Тесты:
    url(
        r'^list/in_progress/$',
        views.task_list_in_progress,
        name='list_in_progress'
    ),
    # tasks/list/enqueued/ Список заданий конвертирования (ожидающие выполнения)
    # Тесты:
    url(
        r'^list/enqueued/$',
        views.task_list_enqueued,
        name='list_enqueued'
    ),
    # tasks/e0593092-fbc5-4b20-99f4-677f8954220f/...
    url(
        r'^(?P<task_id>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/',
        include([
            # tasks/e0593092-fbc5-4b20-99f4-677f8954220f/show/ Описание одного задания
            # Тесты:
            url(
                r'^show/$',
                views.task_show,
                name='show'
            )
        ])
    )
]

urlpatterns = [
    url(r'^tasks/', include((task_patterns, 'task', 'task')))
]
