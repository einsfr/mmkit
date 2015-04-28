from django.core import paginator


def get_page(query_set, page, per_page):
    paginator_instance = paginator.Paginator(query_set, per_page)
    try:
        page = paginator_instance.page(page)
    except paginator.PageNotAnInteger:
        page = paginator_instance.page(1)
    except paginator.EmptyPage:
        page = paginator_instance.page(paginator_instance.num_pages)
    return page