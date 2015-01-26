from django import template
from django.core import paginator
from django.conf import settings
from django.core import urlresolvers

from efsw.common import default_settings

register = template.Library()


def _prepare(page_instance: paginator.Page, page_url_name: str) -> list:
    """
    Формирует список элементов для отображения в листалке.

    Формат результата:
    [
        {
            'text': 'Текст ссылки',
            'title': 'Описание ссылки',
            'url': 'Ссылка',
            'active': True #  Если страница активная, иначе - False
        },
        . . .
    ]
    """
    items = []
    neighbours_count = getattr(settings, 'EFSW_COMM_PAGIN_NEIGHBOURS_COUNT', default_settings.EFSW_COMM_PAGIN_NEIGHBOURS_COUNT)
    page_count = page_instance.paginator.num_pages
    current_page = page_instance.number
    if page_instance.has_previous():
        range_start = current_page - neighbours_count
        if range_start <= 0:
            range_start = 1
        if range_start > 1:
            items.append({
                'text': '1',
                'title': 'Первая страница',
                'url': urlresolvers.reverse(page_url_name, args=(1, )),
                'active': False,
            })
        items.append({
            'text': getattr(settings, 'EFSW_COMM_PAGIN_PREV_TEXT', default_settings.EFSW_COMM_PAGIN_PREV_TEXT),
            'title': 'Предыдущая страница',
            'url': urlresolvers.reverse(page_url_name, args=(current_page - 1, )),
            'active': False,
        })
        for i in range(range_start, current_page):
            items.append({
                'text': str(i),
                'title': 'Страница {0}'.format(i),
                'url': urlresolvers.reverse(page_url_name, args=(i, )),
                'active': False,
            })
    items.append({
        'text': str(current_page),
        'title': 'Страница {0}'.format(current_page),
        'url': '#',
        'active': True,
    })
    if page_instance.has_next():
        range_end = current_page + neighbours_count
        if range_end > page_count:
            range_end = page_count
        for i in range(current_page + 1, range_end + 1):
            items.append({
                'text': str(i),
                'title': 'Страница {0}'.format(i),
                'url': urlresolvers.reverse(page_url_name, args=(i, )),
                'active': False,
            })
        items.append({
            'text': getattr(settings, 'EFSW_COMM_PAGIN_NEXT_TEXT', default_settings.EFSW_COMM_PAGIN_NEXT_TEXT),
            'title': 'Следующая страница',
            'url': urlresolvers.reverse(page_url_name, args=(current_page + 1, )),
            'active': False,
        })
        if range_end < page_count:
            items.append({
                'text': str(page_count),
                'title': 'Последняя страница',
                'url': urlresolvers.reverse(page_url_name, args=(page_count, )),
                'active': False,
            })

    return items


@register.inclusion_tag('common/pagination.html')
def pagination(page_instance, page_url_name):
    if not isinstance(page_instance, paginator.Page):
        msg = "Тэг 'pagination' требует экземпляр класса django.core.paginator.Page, предоставлено: {0}".format(
            type(page_instance)
        )
        raise TypeError(msg)

    return {'items': _prepare(page_instance, page_url_name)}