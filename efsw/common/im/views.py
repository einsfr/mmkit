from django import shortcuts
from django.conf import settings
from django.views.decorators import http
from django.contrib.auth.decorators import permission_required, login_required

from efsw.common.im import models
from efsw.common.im import forms
from efsw.common.http.response import JsonWithStatusResponse
from efsw.common.http.decorators import require_ajax
from efsw.common import errors as common_errors


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
    if not user.is_authenticated():
        raise RuntimeError(common_errors.USER_NOT_AUTHENTICATED)
