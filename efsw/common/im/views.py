from django import shortcuts
from django.conf import settings
from django.views.decorators import http
from django.contrib.auth.decorators import permission_required
from django.utils import timezone

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
    return shortcuts.render(request, 'common/im/conversation_list.html')


@require_ajax
@http.require_GET
@permission_required('common.receive_message', raise_exception=True)
def conversation_list_json(request):
    user = request.user
    conversations = models.Conversation.objects.filter(
        participants__contains=[user.id]
    ).order_by('-last_message__message__sent').select_related('last_message__message')
    newest_message_dt = max([c.last_message.message.sent for c in conversations])
    im_update_channel = models.IMUpdateChannel(user=user, newest_message_dt=newest_message_dt,
                                               last_time_used=timezone.now())
    im_update_channel.save()
    request.session['im_update_channel_id'] = im_update_channel.id


@require_ajax
@http.require_GET
@permission_required('common.receive_message', raise_exception=True)
def conversation_list_updates_json(request):
    pass
