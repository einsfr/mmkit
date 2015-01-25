from django import template
from django.core import paginator
from django.conf import settings
from django.core import urlresolvers

from efsw.common import default_settings

register = template.Library()


@register.inclusion_tag('common/pagination.html')
def pagination(page_instance, page_url_name):
    if not isinstance(page_instance, paginator.Page):
        msg = "Тэг pagination требует экземпляр класса django.core.paginator.Page, предоставлено: {0}".format(
            type(page_instance)
        )
        raise TypeError(msg)
    items = {}
    nc = getattr(settings, 'EFSW_COMM_PAGIN_NEIGHBOURS_COUNT', default_settings.EFSW_COMM_PAGIN_NEIGHBOURS_COUNT)
    if (page_instance.number > nc + 1) and \
            getattr(settings, 'EFSW_COMM_PAGIN_ALWAYS_SHOW_FIRST', default_settings.EFSW_COMM_PAGIN_ALWAYS_SHOW_FIRST):
        pass

    return {'items': items}