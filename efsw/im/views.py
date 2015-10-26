from django import shortcuts
from django.conf import settings
from django.views.decorators import http
from django.contrib.auth.decorators import permission_required
from django.utils import timezone

from efsw.im import models
from efsw.im import forms
from efsw.common.http.response import JsonWithStatusResponse
from efsw.common.http.decorators import require_ajax
from efsw.accounts.utils import format_username


@http.require_GET
@permission_required('common.send_message')
def message_new(request):
    return shortcuts.render(request, 'im/message_new.html', {
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
    return shortcuts.render(request, 'im/conversation_list.html')


def _prepare_conversation_for_json(conversation_dict):
    return {
        'id': str(conversation_dict['id']),
        'type': conversation_dict['conv_type'],
        'lm_content': conversation_dict['last_message__message__content'],
        'lm_sent': timezone.localtime(conversation_dict['last_message__message__sent']).isoformat(),
        'lm_read': timezone.localtime(
            conversation_dict['last_message__message__read']
        ).isoformat() if conversation_dict['last_message__message__read'] is not None else None,
        'lm_sender_repr': format_username(
            username=conversation_dict['last_message__message__sender__username'],
            first_name=conversation_dict['last_message__message__sender__first_name'],
            last_name=conversation_dict['last_message__message__sender__last_name']
        ),
        'lm_sender_is_active': conversation_dict['last_message__message__sender__is_active']
    }


@require_ajax
@http.require_GET
@permission_required('common.receive_message', raise_exception=True)
def conversation_list_json(request):
    user = request.user
    conversations = list(models.Conversation.objects.filter(
        participants__contains=[user.id]
    ).order_by('-last_message__message__sent').select_related(
        'last_message__message', 'last_message__message__sender'
    ).values(
        'id', 'conv_type', 'last_message__message__content', 'last_message__message__sent',
        'last_message__message__read', 'last_message__message__sender__username',
        'last_message__message__sender__first_name', 'last_message__message__sender__last_name',
        'last_message__message__sender__is_active',
    ))
    newest_message_dt = max([c['last_message__message__sent'] for c in conversations])
    im_update_channel = models.IMUpdateChannel(user=user, newest_message_dt=newest_message_dt,
                                               last_time_used=timezone.now())
    im_update_channel.save()
    request.session['im_update_channel_id'] = str(im_update_channel.id)
    return JsonWithStatusResponse(list(map(_prepare_conversation_for_json, conversations)))


@require_ajax
@http.require_GET
@permission_required('common.receive_message', raise_exception=True)
def conversation_list_updates_json(request):
    pass
