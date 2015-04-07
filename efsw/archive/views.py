import json

from django.views import generic
from django import shortcuts
from django.core import paginator
from django.views.decorators import http
from django.conf import settings
from django.core import urlresolvers
from django.views.decorators import csrf
from django.db import IntegrityError

from efsw.archive import models
from efsw.archive import forms
from efsw.archive import default_settings as archive_default_settings
from efsw.common import default_settings as common_default_settings
from efsw.common.search import elastic
from efsw.common.datetime import period
from efsw.common.search.query import EsSearchQuery
from efsw.common.http.response import JsonWithStatusResponse
from efsw.common.utils import urlformatter


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


def _get_json_item_not_found(item_id):
    return JsonWithStatusResponse(
        'Ошибка: элемент с ID "{0}" не существует'.format(item_id),
        JsonWithStatusResponse.STATUS_ERROR
    )


# ------------------------- Общие -------------------------


def search(request):
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


# ------------------------- Item -------------------------


def item_list(request, page='1'):
    items_all = models.Item.objects.all().order_by('-pk').select_related('category')
    items_page = _get_item_list_page(items_all, page)
    return shortcuts.render(request, 'archive/item_list.html', {'items': items_page})


@http.require_GET
def item_new(request):
    form = forms.ItemCreateForm()
    return shortcuts.render(request, 'archive/item_new.html', {'form': form})


@http.require_POST
def item_create(request):
    form = forms.ItemCreateForm(request.POST)
    if form.is_valid():
        item = form.save()
        models.ItemLog.log_item_add(item, request)
        return shortcuts.redirect(item.get_absolute_url())
    else:
        return shortcuts.render(request, 'archive/item_new.html', {'form': form})


@csrf.ensure_csrf_cookie
def item_show(request, item_id):
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
    return shortcuts.render(request, 'archive/item_show.html', {
        'object': item,
        'log_msgs': log_msgs,
        'has_more_log_msgs': has_more_log_msgs,
        'location_add_form': forms.ItemUpdateAddStorageForm()
    })


def item_show_json(request, item_id):
    pass


def item_includes_list_json(request, item_id):
    pass


@http.require_POST
def item_includes_update_json(request, item_id):
    pass


def item_locations_list_json(request, item_id):
    pass


@http.require_POST
def item_locations_update_json(request, item_id):
    pass


def item_logs_list(request, item_id):
    item = shortcuts.get_object_or_404(models.Item, pk=item_id)
    log_msgs = item.log.order_by('-pk').all()
    return shortcuts.render(
        request,
        'archive/item_logs_list.html',
        {
            'item': item,
            'log_msgs': log_msgs,
        }
    )


@http.require_GET
def item_edit(request, item_id):
    item = shortcuts.get_object_or_404(models.Item, pk=item_id)
    form = forms.ItemUpdateForm(instance=item)
    return shortcuts.render(request, 'archive/item_edit.html', {'form': form})


@http.require_POST
def item_update(request, item_id):
    item = shortcuts.get_object_or_404(models.Item, pk=item_id)
    form = forms.ItemUpdateForm(request.POST, instance=item)
    if form.is_valid():
        item = form.save()
        models.ItemLog.log_item_update(item, request)
        return shortcuts.redirect(item.get_absolute_url())
    else:
        return shortcuts.render(request, 'archive/item_edit.html', {'form': form})


# ------------------------- ItemCategory -------------------------















def category_items_list(request, category='0', page='1'):
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


@http.require_http_methods(["GET"])
def item_includes_get(request, item_id):

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
    include_id = request.GET.get('id', None)
    if include_id is None:
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
        includes_ids = json.loads(request.POST.get('includes', ''))
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
            'storage': l.storage.name,
            'storage_id': l.storage.id,
        }
        if l.storage.is_online_type():
            d['location'] = l.get_url().format_win()
        else:
            d['location'] = l.location
        response.append(d)
    return JsonWithStatusResponse(response)


@http.require_http_methods(["POST"])
def item_locations_post(request, item_id):
    try:
        item = models.Item.objects.get(pk=item_id)
    except models.Item.DoesNotExist:
        return _get_json_item_not_found(item_id)
    try:
        locations = json.loads(request.POST.get('locations', ''))
    except [ValueError, KeyError]:
        return JsonWithStatusResponse(
            'Неверный формат запроса',
            JsonWithStatusResponse.STATUS_ERROR
        )
    if len(locations) == 0:
        models.ItemLocation.objects.filter(item=item).delete()
        return JsonWithStatusResponse()
    storage_ids = set([l['storage_id'] for l in locations])
    storages = models.Storage.objects.filter(id__in=storage_ids)
    if len(storage_ids) != len(storages):
        return JsonWithStatusResponse(
            'Используется несуществующее хранилище',
            JsonWithStatusResponse.STATUS_ERROR
        )
    storages_dict = dict([(s.id, s) for s in storages])
    leftover_locations = [l['id'] for l in locations if l['id']]
    models.ItemLocation.objects.filter(item=item).exclude(pk__in=leftover_locations).delete()
    for l in locations:
        if l['id'] != 0:
            continue
        l_obj = models.ItemLocation()
        l_obj.storage = storages_dict[l['storage_id']]
        l_obj.item = item
        l_obj.location = l['location']
        try:
            l_obj.save()
        except IntegrityError:
            return JsonWithStatusResponse(
                'Элемент не может иметь несколько расположений в одном хранилище',
                JsonWithStatusResponse.STATUS_ERROR
            )
    return JsonWithStatusResponse()


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


def _get_json_storage_not_found(storage_id):
    return JsonWithStatusResponse(
        'Ошибка: хранилище с ID "{0}" не существует'.format(storage_id),
        JsonWithStatusResponse.STATUS_ERROR
    )


def storage_get(request):

    def format_storage_dict(s):
        return_dict = {
            'id': s.id,
            'name': s.name,
            'disable_location': s.is_online_master_type(),
        }
        if s.is_online_type():
            return_dict['base_url'] = urlformatter.format_url(s.base_url).format_win()
        else:
            return_dict['base_url'] = ''
        return return_dict

    storage_id = request.GET.get('id', None)
    if storage_id is None:
        return JsonWithStatusResponse([
            format_storage_dict(s)
            for s in models.Storage.objects.all()
        ])
    else:
        try:
            storage = models.Storage.objects.get(pk=storage_id)
        except models.Storage.DoesNotExist:
            return _get_json_storage_not_found(storage_id)
        return JsonWithStatusResponse(format_storage_dict(storage))