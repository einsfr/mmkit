from django import shortcuts
from django.conf import settings
from django.views.decorators import http
from django.contrib.auth.decorators import permission_required, login_required
from django.db.models import Max

from efsw.common.im import models
from efsw.common.im import forms
from efsw.common.http.response import JsonWithStatusResponse
from efsw.common.http.decorators import require_ajax


@http.require_GET
@permission_required('common.add_message')
def message_new(request):
    return shortcuts.render(request, 'common/im/message_new.html', {
        'form': forms.MessageCreateForm()
    })


@require_ajax
@http.require_POST
@permission_required('common.add_message', raise_exception=True)
def message_create_json(request):
    pass


@http.require_GET
@login_required()
def conversation_list(request):
    user = request.user
    conversations = models.Conversation.objects.filter(
        participants__contains=[user.id]
    ).annotate(last_update=Max('messages__sended')).order_by('-last_update')
    return shortcuts.render(request, 'common/im/conversation_list.html', {
        'conversations': list(conversations)
    })

