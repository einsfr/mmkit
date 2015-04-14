import json

from django import shortcuts
from django.core import paginator
from django.views.decorators import http
from django.conf import settings
from django.core import urlresolvers
from django.views.decorators import csrf
from django.db import IntegrityError, transaction

from efsw.archive import models
from efsw.archive import forms
from efsw.archive import default_settings as archive_default_settings
from efsw.common import default_settings as common_default_settings
from efsw.common.search import elastic
from efsw.common.datetime import period
from efsw.common.search.query import EsSearchQuery
from efsw.common.http.response import JsonWithStatusResponse
from efsw.common.utils import urlformatter


def _get_item_list_page(items, page):
    per_page = getattr(
        settings,
        'EFSW_ARCH_ITEM_LIST_PER_PAGE',
        archive_default_settings.EFSW_ARCH_ITEM_LIST_PER_PAGE
    )
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


def _get_json_item_not_found(item_id):
    return JsonWithStatusResponse(
        'Ошибка: элемент с ID "{0}" не существует'.format(item_id),
        JsonWithStatusResponse.STATUS_ERROR
    )


def _get_json_wrong_format():
    return JsonWithStatusResponse(
        'Неверный формат запроса',
        JsonWithStatusResponse.STATUS_ERROR
    )


def _format_item_dict(i):
    return {
        'id': i.id,
        'name': i.name,
        'url': i.get_absolute_url(),
    }


def _get_json_storage_not_found(storage_id):
    return JsonWithStatusResponse(
        'Ошибка: хранилище с ID "{0}" не существует'.format(storage_id),
        JsonWithStatusResponse.STATUS_ERROR
    )


def _check_include(item, include):
    return


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
        'item': item,
        'log_msgs': log_msgs,
        'has_more_log_msgs': has_more_log_msgs,
        'location_add_form': forms.ItemUpdateAddStorageForm()
    })


def item_includes_list_json(request):
    item_id = request.GET.get('id', None)
    try:
        item = models.Item.objects.get(pk=item_id)
    except models.Item.DoesNotExist:
        return _get_json_item_not_found(item_id)
    includes_list = [
        _format_item_dict(i)
        for i in item.includes.all()
    ]
    return JsonWithStatusResponse(includes_list)


def item_includes_check_json(request):
    item_id = request.GET.get('id', None)
    include_id = request.GET.get('include_id', None)
    try:
        if int(item_id) == int(include_id):
            return JsonWithStatusResponse(
                'Элемент не может быть включён сам в себя',
                JsonWithStatusResponse.STATUS_ERROR
            )
    except ValueError:
        return JsonWithStatusResponse(
            'Идентификатор должен быть целым числом',
            JsonWithStatusResponse.STATUS_ERROR
        )
    try:
        item = models.Item.objects.get(pk=item_id)
    except models.Item.DoesNotExist:
        return _get_json_item_not_found(item_id)
    try:
        include_item = models.Item.objects.get(pk=include_id)
    except models.Item.DoesNotExist:
        return _get_json_item_not_found(include_id)
    check_result = _check_include(item, include_item)
    if check_result is not None:
        return JsonWithStatusResponse(check_result, JsonWithStatusResponse.STATUS_ERROR)
    return JsonWithStatusResponse(_format_item_dict(include_item))


@http.require_POST
def item_includes_update_json(request):
    item_id = request.GET.get('id', None)
    try:
        item = models.Item.objects.get(pk=item_id)
    except models.Item.DoesNotExist:
        return _get_json_item_not_found(item_id)
    post_includes = request.POST.get('includes', None)
    if post_includes is None:
        return _get_json_wrong_format()
    try:
        includes_ids = set(json.loads(post_includes))
    except ValueError:
        return _get_json_wrong_format()
    old_includes_ids = set([i.id for i in item.includes.all()])
    removing_includes_ids = old_includes_ids.difference(includes_ids)
    removing_includes_objects = list(models.Item.objects.filter(id__in=removing_includes_ids))
    # Если мы только всё убираем - можно немного проще
    if len(includes_ids) == 0:
        item.includes.clear()
        models.ItemLog.log_item_include_update(removing_includes_objects + [item], request)
        return JsonWithStatusResponse()
    # Сначала удаляем всё, что нужно удалить
    item.includes.remove(*removing_includes_objects)
    models.ItemLog.log_item_include_update(removing_includes_objects + [item], request)
    # Потом добавляем всё, что нужно добавить
    adding_includes_ids = includes_ids.difference(old_includes_ids)
    # Убираем самого себя из включений, если есть
    if item.id in adding_includes_ids:
        adding_includes_ids.remove(item.id)
    adding_includes_objects = [
        o
        for o in models.Item.objects.filter(id__in=adding_includes_ids)
        if _check_include(item, o) is None
    ]
    item.includes.add(*adding_includes_objects)
    models.ItemLog.log_item_include_update(adding_includes_objects, request)
    return JsonWithStatusResponse()


def item_locations_list_json(request):

    def _format_location_dict(l):
        d = {
            'id': l.id,
            'storage': l.storage.name,
            'storage_id': l.storage.id,
        }
        if l.storage.is_online_type():
            d['location'] = l.get_url().format_win()
        else:
            d['location'] = l.location
        return d

    item_id = request.GET.get('id', None)
    try:
        item = models.Item.objects.get(pk=item_id)
    except models.Item.DoesNotExist:
        return _get_json_item_not_found(item_id)
    locations_list = [
        _format_location_dict(l)
        for l in item.locations.all().select_related('storage')
    ]
    return JsonWithStatusResponse(locations_list)


@http.require_POST
def item_locations_update_json(request):
    item_id = request.GET.get('id', None)
    try:
        item = models.Item.objects.get(pk=item_id)
    except models.Item.DoesNotExist:
        return _get_json_item_not_found(item_id)
    post_locations = request.POST.get('locations', None)
    if post_locations is None:
        return _get_json_wrong_format()
    try:
        locations = json.loads(post_locations)
    except ValueError:
        return _get_json_wrong_format()
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
            with transaction.atomic():
                l_obj.save()
        except IntegrityError:
            return JsonWithStatusResponse(
                'Элемент не может иметь несколько расположений в одном хранилище',
                JsonWithStatusResponse.STATUS_ERROR
            )
    return JsonWithStatusResponse()


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


def category_list(request):
    categories = models.ItemCategory.objects.all().order_by('name')
    return shortcuts.render(request, 'archive/category_list.html', {
        'categories': categories,
    })


@http.require_GET
def category_new(request):
    form = forms.ItemCategoryForm()
    return shortcuts.render(request, 'archive/category_new.html', {'form': form})


@http.require_POST
def category_create(request):
    form = forms.ItemCategoryForm(request.POST)
    if form.is_valid():
        form.save()
        return shortcuts.redirect(urlresolvers.reverse('efsw.archive:category:list'))
    else:
        return shortcuts.render(request, 'archive/category_new.html', {'form': form})


def category_items_list(request, category_id, page='1'):
    cat = shortcuts.get_object_or_404(models.ItemCategory, pk=category_id)
    items_all = cat.items.all().order_by('-pk')
    items_page = _get_item_list_page(items_all, page)
    return shortcuts.render(request, 'archive/category_items_list.html', {
        'items': items_page,
        'category': cat
    })


@http.require_GET
def category_edit(request, category_id):
    cat = shortcuts.get_object_or_404(models.ItemCategory, pk=category_id)
    form = forms.ItemCategoryForm(request.POST, instance=cat)
    return shortcuts.render(request, 'archive/category_edit.html', {'form': form})


@http.require_POST
def category_update(request, category_id):
    cat = shortcuts.get_object_or_404(models.ItemCategory, pk=category_id)
    form = forms.ItemCategoryForm(request.POST, instance=cat)
    if form.is_valid():
        form.save()
        return shortcuts.redirect(urlresolvers.reverse('efsw.archive:category:list'))
    else:
        return shortcuts.render(request, 'archive/category_edit.html', {'form': form})


# ------------------------- Storage -------------------------


def storage_show_json(request):

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
    try:
        storage = models.Storage.objects.get(pk=storage_id)
    except models.Storage.DoesNotExist:
        return _get_json_storage_not_found(storage_id)
    return JsonWithStatusResponse(format_storage_dict(storage))