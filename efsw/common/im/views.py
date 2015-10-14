from django import shortcuts
from django.conf import settings
from django.views.decorators import http

from efsw.common.im import models
from efsw.common.im import forms
from efsw.common.http.response import JsonWithStatusResponse
from efsw.common.http.decorators import require_ajax
from efsw.common import errors as common_errors


@http.require_GET
def message_new(request):
    return shortcuts.render(request, 'common/im/message_new.html', {
        'form': forms.MessageCreateForm()
    })


@require_ajax
@http.require_POST
def message_create_json(request):
    pass


@http.require_GET
def conversation_list(request):
    user = request.user
    if not user.is_authenticated():
        raise RuntimeError(common_errors.USER_NOT_AUTHENTICATED)
