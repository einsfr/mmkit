from django import shortcuts
from django.conf import settings
from django.views.decorators import http
from django.contrib.auth.decorators import permission_required

from efsw.common.im import models
from efsw.common.im import forms
from efsw.common.http.response import JsonWithStatusResponse
from efsw.common.http.decorators import require_ajax
from efsw.common.utils import params


@http.require_GET
@permission_required('common.send_message')
def message_new(request):
    return shortcuts.render(request, 'common/im/message_new.html', {
        'form': forms.MessageCreateForm()
    })


@require_ajax
@http.require_POST
@permission_required('common.send_message', raise_exception=True)
def message_create_json(request):
    pass


@http.require_GET
@permission_required('common.receive_message')
def conversation_list(request):
    user = request.user
    conversations = models.Conversation.objects.filter(
        participants__contains=[user.id]
    ).order_by('-last_message__message__sent').select_related('last_message__message')
    return shortcuts.render(request, 'common/im/conversation_list.html')


@require_ajax
@http.require_GET
@permission_required('common.receive_message')
def conversation_list_json(request):
    user = request.user
    parse_result = params.parse_params_or_get_json_error(
        request.GET, last_update=r'(?:^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d*)?$)|(?:^$)'
    )
    if type(parse_result) != dict:
        return parse_result
