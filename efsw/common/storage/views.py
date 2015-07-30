from django import shortcuts
from django.conf import settings
from django.views.decorators import http


@http.require_GET
def nav_ls_json(request):
    pass
