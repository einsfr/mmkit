import json

from django.views import generic
from django import shortcuts
from django.http import HttpResponse, HttpResponseBadRequest
from django.core import paginator
from django.views.decorators import http
from django.conf import settings
from django.core import urlresolvers
from django.views.decorators import csrf

from efsw.archive import models
from efsw.archive import forms
from efsw.archive import default_settings as archive_default_settings
from efsw.common import default_settings as common_default_settings
from efsw.common.search import elastic
from efsw.common.datetime import period
from efsw.common.search.query import EsSearchQuery
from efsw.common.http.response import JsonWithStatusResponse


def _get_item_page(items, page, per_page):
    pagin = paginator.Paginator(items, per_page)
    try:
        items_page = pagin.page(page)
    except paginator.PageNotAnInteger:
        # Если параметр page не является целым числом - показать первую страницу
        items_page = pagin.page(1)
    except paginator.EmptyPage:
        # Если указанная страница - пустая (т.е. находится вне диапазона страниц) - показать последнюю страницу
        items_page = pagin.page(pagin.num_pages)
    return items_page


def _get_item_list_page(items, page):
    per_page = getattr(
        settings,
        'EFSW_ARCH_ITEM_LIST_PER_PAGE',
        archive_default_settings.EFSW_ARCH_ITEM_LIST_PER_PAGE
    )
    return _get_item_page(items, page, per_page)


def item_list(request, page='1'):
    items_all = models.Item.objects.all().order_by('-pk').select_related('category')
    items_page = _get_item_list_page(items_all, page)
    return shortcuts.render(request, 'archive/item_list.html', {'items': items_page})


def item_list_category(request, category='0', page='1'):
    try:
        category_id = int(category)
    except ValueError:
        category_id = 0
    if category_id == 0:
        return item_list(request, page)
    cat = shortcuts.get_object_or_404(models.ItemCategory, pk=category_id)
    items_all = cat.items.all().order_by('-pk')
    items_page = _get_item_list_page(items_all, page)
    return shortcuts.render(request, 'archive/item_list_category.html', {'items': items_page, 'category': cat})


def item_detail(request, item_id):
    item = shortcuts.get_object_or_404(
        models.Item.objects.select_related('category').prefetch_related('includes', 'included_in'),
        pk=item_id
    )
    log_msg_count = item.log.count()
    max_count = getattr(
        settings,
        'EFSW_ARCH_ITEM_DETAIL_LOG_MESSAGES_COUNT',
        archive_default_settings.EFSW_ARCH_ITEM_DETAIL_LOG_MESSAGES_COUNT
    )
    if log_msg_count <= max_count:
        log_msgs = item.log.order_by('-pk').all().select_related('user')
        has_more_log_msgs = False
    else:
        log_msgs = item.log.order_by('-pk').all().select_related('user')[0:3]
        has_more_log_msgs = True
    return shortcuts.render(request, 'archive/item_detail.html', {
        'object': item,
        'log_msgs': log_msgs,
        'has_more_log_msgs': has_more_log_msgs,
    })


def item_log(request, item_id):
    item = shortcuts.get_object_or_404(models.Item, pk=item_id)
    log_msgs = item.log.order_by('-pk').all()
    return shortcuts.render(
        request,
        'archive/item_log.html',
        {
            'item': item,
            'log_msgs': log_msgs,
        }
    )


def item_add(request):
    if request.method == 'POST':
        form = forms.ItemCreateForm(request.POST)
        if form.is_valid():
            item = form.save()
            models.ItemLog.log_item_add(item, request)
            return shortcuts.redirect(item.get_absolute_url())
    else:
        form = forms.ItemCreateForm()
    return shortcuts.render(request, 'archive/item_form_create.html', {'form': form})


def item_update(request, item_id):
    item = shortcuts.get_object_or_404(models.Item, pk=item_id)
    if request.method == 'POST':
        form = forms.ItemUpdateForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            models.ItemLog.log_item_update(item, request)
            return shortcuts.redirect(item.get_absolute_url())
    else:
        form = forms.ItemUpdateForm(instance=item)
    return shortcuts.render(request, 'archive/item_form_update.html', {'form': form})


def _get_json_item_not_found(item_id):
    return JsonWithStatusResponse(
        'Ошибка: элемент с ID "{0}" не существует'.format(item_id),
        JsonWithStatusResponse.STATUS_ERROR
    )


@http.require_http_methods(["GET"])
def item_includes_get(request, item_id, include_id=0):

    def format_item_dict(i):
        return {
            'id': i.id,
            'name': i.name,
            'url': i.get_absolute_url(),
            'url_title': i.get_absolute_url_title(),
        }

    try:
        item = models.Item.objects.get(pk=item_id)
    except models.Item.DoesNotExist:
        return _get_json_item_not_found(item_id)
    if not include_id:
        includes_list = [
            format_item_dict(i)
            for i in item.includes.all()
        ]
        return JsonWithStatusResponse(includes_list)
    else:
        try:
            include_item = models.Item.objects.get(pk=include_id)
        except models.Item.DoesNotExist:
            return _get_json_item_not_found(include_id)
        include_dict = format_item_dict(include_item)
        return JsonWithStatusResponse(include_dict)


@http.require_http_methods(["POST"])
def item_includes_post(request, item_id):
    try:
        item = models.Item.objects.get(pk=item_id)
    except models.Item.DoesNotExist:
        return _get_json_item_not_found(item_id)
    try:
        includes_ids = json.loads(request.POST.get('data', ''))['includes']
    except [ValueError, KeyError]:
        return JsonWithStatusResponse(
            'Неверный формат запроса',
            JsonWithStatusResponse.STATUS_ERROR
        )
    item.includes.clear()
    # TODO Нужно определить, какие элементы изменяются и внести в лог соответствующие записи
    if len(includes_ids) > 0:
        includes = models.Item.objects.filter(id__in=includes_ids)
        item.includes.add(*includes)
    return JsonWithStatusResponse()


@http.require_http_methods(["GET"])
def item_locations_get(request, item_id):
    try:
        item = models.Item.objects.get(pk=item_id)
    except models.Item.DoesNotExist:
        return _get_json_item_not_found(item_id)
    locations = item.locations.all().select_related('storage')
    response = []
    for l in locations:
        d = {
            'id': l.id,
            'storage': l.storage.name
        }
        if l.storage.is_online_type():
            d['location'] = l.get_url().format_win()
        else:
            d['location'] = l.location
        response.append(d)
    return JsonWithStatusResponse(response)


@http.require_http_methods(["POST"])
def item_locations_post(request, item_id):
    pass


class CategoryListView(generic.ListView):
    queryset = models.ItemCategory.objects.all().order_by('name')
    template_name = 'archive/category_list.html'


class CategoryAddView(generic.CreateView):
    model = models.ItemCategory
    template_name = 'archive/category_form_create.html'
    form_class = forms.ItemCategoryForm
    success_url = urlresolvers.reverse_lazy('efsw.archive:category_list')


class CategoryUpdateView(generic.UpdateView):
    model = models.ItemCategory
    template_name = 'archive/category_form_update.html'
    form_class = forms.ItemCategoryForm
    success_url = urlresolvers.reverse_lazy('efsw.archive:category_list')


@csrf.csrf_exempt
def search(request, page=1):
    es_cm = elastic.get_connection_manager()
    es = es_cm.get_es()
    es_status = es_cm.get_es_status()
    if es is None or (es_status != 'yellow' and es_status != 'green'):
        return shortcuts.render(request, 'archive/search_offline.html', status=500)

    form = forms.ArchiveSearchForm(request.GET)
    if form.is_valid():
        sq = EsSearchQuery(es_cm, 'efswarchitem', 'item')
        if not form.cleaned_data['q'] and not form.cleaned_data['c'] and not form.cleaned_data['p']:
            return shortcuts.render(request, 'archive/search.html', {'form': form, 'search_performed': False})
        query = form.cleaned_data['q']
        if query:
            sq.query_multi_match(str(query), ['name', 'description', 'author'])
        order = form.cleaned_data['o']
        if order == forms.ArchiveSearchForm.ORDER_BY_CREATED_ASC:
            sq.sort_field('created')
        elif order == forms.ArchiveSearchForm.ORDER_BY_CREATED_DESC:
            sq.sort_field('created', sq.ORDER_DESC)
        categories = form.cleaned_data['c']
        try:
            date_period = period.DatePeriod.get(int(form.cleaned_data['p']), strict=True)
        except (period.PeriodDoesNotExist, ValueError):
            date_period = None
        if categories:
            sq.filter_terms('category', [x.id for x in categories])
        if date_period:
            sq.filter_range('created', gte=date_period[0].isoformat(), lte=date_period[1].isoformat())
        search_size = getattr(
            settings,
            'EFSW_ELASTIC_MAX_SEARCH_RESULTS',
            common_default_settings.EFSW_ELASTIC_MAX_SEARCH_RESULTS
        )
        sq.from_size(size_param=search_size)
        result = sq.get_result()
        hits = result['hits']
        if hits['total']:
            hits_ids = [h['_id'] for h in hits['hits']]
            items_dict = dict(
                map(lambda x: (str(x.id), x), models.Item.objects.filter(id__in=hits_ids).select_related('category'))
            )
            items = list(filter(lambda x: x is not None, [items_dict.get(x) for x in hits_ids]))
        else:
            items = None
        return shortcuts.render(
            request,
            'archive/search.html',
            {
                'form': form,
                'items': items,
                'hits': hits['total'],
                'search_size': search_size,
                'search_performed': True
            }
        )
    else:
        return shortcuts.render(request, 'archive/search.html', {'form': form, 'search_performed': False})