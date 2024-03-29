from django.conf.urls import include, url

from efsw.im import views


msg_patterns = [
    # messages/new/
    # Тесты:
    url(
        r'^new/$',
        views.message_new,
        name='new'
    ),
    # messages/create/json/
    # Тесты:
    url(
        r'^create/json/$',
        views.message_create_json,
        name='create_json'
    )
]

conv_patterns = [
    # conversations/list/
    # Тесты:
    url(
        r'^list/$',
        views.conversation_list,
        name='list'
    ),
    # conversations/list/json/
    # Тесты:
    url(
        r'^list/json/$',
        views.conversation_list_json,
        name='list_json'
    )
]

urlpatterns = [
    url(r'^messages/', include((msg_patterns, 'message', 'message'))),
    url(r'^conversations/', include((conv_patterns, 'conversation', 'conversation')))
]
