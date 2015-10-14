from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required

from efsw.common.im import views


msg_patterns = [
    # messages/new/
    # Тесты:
    url(
        r'^new/$',
        login_required()(views.message_new),
        name='new'
    ),
    # messages/create/json/
    # Тесты:
    url(
        r'^create/json/$',
        login_required()(views.message_create_json),
        name='create_json'
    )
]

conv_patterns = [
    # conversations/list/
    # Тесты:
    url(
        r'^list/$',
        login_required()(views.conversation_list),
        name='list'
    )
]

urlpatterns = [
    url(r'^messages/', include((msg_patterns, 'message', 'message'))),
    url(r'^conversations/', include((conv_patterns, 'conversation', 'conversation')))
]
