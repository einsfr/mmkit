import json
import datetime

from django import shortcuts
from django.views.decorators import http
from django.conf import settings
from django.core import urlresolvers

from efsw.archive import models
from efsw.archive import forms
from efsw.common.search import elastic
from efsw.common.datetime import period
from efsw.common.search.query import EsSearchQuery
from efsw.common.http.response import JsonWithStatusResponse
from efsw.common.db import pagination
from efsw.common import models as common_models
from efsw.common.http.decorators import require_ajax


def _get_json_item_not_found(item_id):
    return JsonWithStatusResponse.error(
        'Ошибка: элемент с ID "{0}" не существует.'.format(item_id),
        'item_not_found'
    )


def _get_json_item_wrong_id(item_id):
    return JsonWithStatusResponse.error(
        'Ошибка: идентификатор элемента должен быть целым числом, предоставлено: "{0}".'.format(item_id),
        'id_not_int'
    )


def _get_json_wrong_format():
    return JsonWithStatusResponse.error('Неверный формат запроса.', 'wrong_format')


def _format_item_dict(i):
    return {
        'id': i.id,
        'name': i.name,
        'url': i.get_absolute_url(),
    }


def _get_json_storage_not_found(storage_id):
    return JsonWithStatusResponse.error(
        'Ошибка: хранилище с ID "{0}" не существует.'.format(storage_id),
        'storage_not_found'
    )


def _check_include(item, include):
    return None


def _check_include_in(item, include_in):
    return None


def _get_json_category_not_found(item_id):
    return JsonWithStatusResponse.error(
        'Ошибка: категория с ID "{0}" не существует.'.format(item_id),
        'category_not_found'
    )


def _get_json_category_wrong_id(item_id):
    return JsonWithStatusResponse.error(
        'Ошибка: идентификатор категории должен быть целым числом, предоставлено: "{0}".'.format(item_id),
        'id_not_int'
    )


# ------------------------- Общие -------------------------

@http.require_GET
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
            if form.cleaned_data['ph']:
                sq.query_multi_match(
                    str(query).lower().replace('ё', 'е'), ['name', 'description', 'author'],
                    query_type=EsSearchQuery.MULTI_MATCH_QUERY_TYPE_PHRASE
                )
            else:
                sq.query_multi_match(str(query).lower().replace('ё', 'е'), ['name', 'description', 'author'])
        order = form.cleaned_data['o']
        if order == forms.ArchiveSearchForm.ORDER_BY_CREATED_ASC:
            sq.sort_field('created')
        elif order == forms.ArchiveSearchForm.ORDER_BY_CREATED_DESC:
            sq.sort_field('created', sq.ORDER_DESC)
        categories = form.cleaned_data['c']
        if form.cleaned_data['p'] == 'custom':
            if not form.cleaned_data['p_s'] and not form.cleaned_data['p_e']:
                date_period = None
            else:
                p_s = form.cleaned_data['p_s']
                p_e = form.cleaned_data['p_e']
                date_period = (
                    p_s if p_s else datetime.date.min,
                    p_e if p_e else datetime.date.today()
                )
        else:
            try:
                date_period = period.DatePeriod.get(int(form.cleaned_data['p']), strict=True)
            except (period.PeriodDoesNotExist, ValueError):
                date_period = None
        if categories:
            sq.filter_terms('category', [x.id for x in categories])
        if date_period:
            sq.filter_range('created', gte=date_period[0].isoformat(), lte=date_period[1].isoformat())
        search_size = settings.EFSW_ELASTIC_MAX_SEARCH_RESULTS
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


@http.require_GET
def item_list(request, page='1'):
    items_all = models.Item.objects.all().order_by('-pk').select_related('category')
    items_page = pagination.get_page(items_all, page, settings.EFSW_ARCH_ITEM_LIST_PER_PAGE)
    return shortcuts.render(request, 'archive/item_list.html', {'items': items_page})


@http.require_GET
def item_new(request):
    form = forms.ItemCreateForm()
    return shortcuts.render(request, 'archive/item_new.html', {'form': form})


@require_ajax
@http.require_POST
def item_create_json(request):
    form = forms.ItemCreateForm(request.POST)
    if form.is_valid():
        item = form.save()
        models.ItemLog.log_item_add(item, request)
        return JsonWithStatusResponse.ok(urlresolvers.reverse('efsw.archive:item:edit_locations', args=(item.id, )))
    else:
        return JsonWithStatusResponse.error({'errors': form.errors.as_json()})


@http.require_GET
def item_show(request, item_id):
    return item_show_properties(request, item_id)


@http.require_GET
def item_show_properties(request, item_id):
    item = shortcuts.get_object_or_404(
        models.Item.objects.select_related('category'),
        pk=item_id
    )
    return shortcuts.render(request, 'archive/item_show_properties.html', {
        'item': item
    })


@http.require_GET
def item_show_locations(request, item_id):
    item = shortcuts.get_object_or_404(
        models.Item.objects.prefetch_related(
            'file_locations', 'file_locations__file_object', 'file_locations__file_object__storage',
        ),
        pk=item_id
    )
    return shortcuts.render(request, 'archive/item_show_locations.html', {
        'item': item
    })


@http.require_GET
def item_show_links(request, item_id):
    item = shortcuts.get_object_or_404(
        models.Item.objects.prefetch_related('includes', 'included_in'),
        pk=item_id
    )
    return shortcuts.render(request, 'archive/item_show_links.html', {
        'item': item
    })


@http.require_GET
def item_show_log(request, item_id):
    item = shortcuts.get_object_or_404(models.Item.objects, pk=item_id)
    return shortcuts.render(request, 'archive/item_show_log.html', {
        'item': item,
        'log': item.log.select_related('user').order_by('-pk').all()
    })


LINK_TYPE_INCLUDED_IN = 1
LINK_TYPE_INCLUDES = 2


@require_ajax
@http.require_GET
def item_check_links_json(request):
    item_id = request.GET.get('id', None)
    inc_id = request.GET.get('include_id', None)
    try:
        inc_type = int(request.GET.get('type', None))
    except ValueError:
        return JsonWithStatusResponse.error('Неизвестный тип связи.', 'unknown_link_type')
    except TypeError:
        return JsonWithStatusResponse.error(
            'Проверьте строку запроса - возможно, не установлен параметр type.',
            'link_type_is_missed'
        )
    try:
        if int(item_id) == int(inc_id):
            return JsonWithStatusResponse.error('Элемент не может быть включён сам в себя.', 'self_self_link')
    except ValueError:
        return JsonWithStatusResponse.error('Идентификатор должен быть целым числом.', 'id_not_int')
    except TypeError:
        return JsonWithStatusResponse.error(
            'Проверьте строку запроса - возможно, не установлен один из параметров id или inc_id.',
            'id_is_missed'
        )
    try:
        item = models.Item.objects.get(pk=item_id)
    except models.Item.DoesNotExist:
        return _get_json_item_not_found(item_id)
    try:
        inc_item = models.Item.objects.get(pk=inc_id)
    except models.Item.DoesNotExist:
        return _get_json_item_not_found(inc_id)
    if inc_type == LINK_TYPE_INCLUDED_IN:
        check_result = _check_include_in(item, inc_item)
    elif inc_type == LINK_TYPE_INCLUDES:
        check_result = _check_include(item, inc_item)
    else:
        return JsonWithStatusResponse.error('Неизвестный тип связи.', 'unknown_link_type')
    if check_result is not None:
        return JsonWithStatusResponse.error(check_result)
    return JsonWithStatusResponse.ok(_format_item_dict(inc_item))


def _log_inc_update(inc_list, request):
    obj_ids_list = []
    obj_list = []
    for i in inc_list:
        if i.id not in obj_ids_list:
            obj_ids_list.append(i.id)
            obj_list.append(i)
    models.ItemLog.log_item_include_update(obj_list, request)


@require_ajax
@http.require_POST
def item_update_links_json(request):
    item_id = request.GET.get('id', None)
    try:
        item = models.Item.objects.get(pk=item_id)
    except models.Item.DoesNotExist:
        return _get_json_item_not_found(item_id)
    except ValueError:
        return _get_json_item_wrong_id(item_id)
    post_includes = request.POST.get('includes', None)
    post_included_in = request.POST.get('included_in', None)
    if post_includes is None or post_included_in is None:
        return _get_json_wrong_format()
    try:
        includes_ids = set(json.loads(post_includes))
        included_in_ids = set(json.loads(post_included_in))
    except ValueError:
        return _get_json_wrong_format()
    log_inc_update = [item]
    old_includes_ids = set([i.id for i in item.includes.all()])
    old_included_in_ids = set([i.id for i in item.included_in.all()])
    removing_includes_obj = list(models.Item.objects.filter(id__in=old_includes_ids.difference(includes_ids)))
    removing_included_in_obj = list(models.Item.objects.filter(id__in=old_included_in_ids.difference(included_in_ids)))
    if len(includes_ids) == 0:
        item.includes.clear()
    else:
        item.includes.remove(*removing_includes_obj)
    log_inc_update = log_inc_update + removing_includes_obj
    if len(included_in_ids) == 0:
        item.included_in.clear()
    else:
        item.included_in.remove(*removing_included_in_obj)
    log_inc_update = log_inc_update + removing_included_in_obj
    if len(includes_ids) == 0 and len(included_in_ids) == 0:
        _log_inc_update(log_inc_update, request)
        return JsonWithStatusResponse.ok()
    adding_includes_ids = includes_ids.difference(old_includes_ids)
    adding_included_in_ids = included_in_ids.difference(old_included_in_ids)
    if item.id in adding_includes_ids:
        adding_includes_ids.remove(item.id)
    if item.id in adding_included_in_ids:
        adding_included_in_ids.remove(item.id)
    adding_includes_obj = list(
        filter(lambda o: _check_include(item, o) is None, models.Item.objects.filter(id__in=adding_includes_ids))
    )
    adding_included_in_obj = list(
        filter(lambda o: _check_include_in(item, o) is None, models.Item.objects.filter(id__in=adding_included_in_ids))
    )
    item.includes.add(*adding_includes_obj)
    log_inc_update = log_inc_update + adding_includes_obj
    item.included_in.add(*adding_included_in_obj)
    log_inc_update = log_inc_update + adding_included_in_obj
    _log_inc_update(log_inc_update, request)
    return JsonWithStatusResponse.ok()


@require_ajax
@http.require_POST
def item_update_locations_json(request):
    item_id = request.GET.get('id', None)
    try:
        item = models.Item.objects.get(pk=item_id)
    except models.Item.DoesNotExist:
        return _get_json_item_not_found(item_id)
    except ValueError:
        return _get_json_item_wrong_id(item_id)
    post_locations = request.POST.get('locations', None)
    if post_locations is None:
        return _get_json_wrong_format()
    try:
        locations = json.loads(post_locations)
    except ValueError:
        return _get_json_wrong_format()
    if len(locations) == 0:
        models.ItemFileLocation.objects.filter(item=item).delete()
        return JsonWithStatusResponse.ok()
    storage_ids_list = [l['storage_id'] for l in locations]
    storage_ids = set(storage_ids_list)
    storages = common_models.FileStorage.objects.filter(id__in=storage_ids)
    if len(storage_ids) != len(storages):
        return JsonWithStatusResponse.error('Используется несуществующее хранилище.', 'storage_not_found')
    if list(filter(lambda s: 'archive' not in s.allowed_usage, storages)):
        return JsonWithStatusResponse.error('Одно или несколько хранилищ не имеют отметки, позволяющей использовать их '
                                            'как архивные.', 'storage_not_allowed')
    storages_dict = dict([(str(s.id), s) for s in storages])
    leftover_locations = [l['id'] for l in locations if l['id']]
    models.ItemFileLocation.objects.filter(item=item).exclude(pk__in=leftover_locations).delete()
    for l in locations:
        if l['id']:
            continue
        storage = storages_dict[l['storage_id']]
        l_obj = models.ItemFileLocation(
            item=item,
            file_object=storage.get_or_create_file_object(l['path'])
        )
        l_obj.save()
    return JsonWithStatusResponse.ok(urlresolvers.reverse('efsw.archive:item:edit_links', args=(item.id, )))


@http.require_GET
def item_edit(request, item_id):
    return item_edit_properties(request, item_id)


@http.require_GET
def item_edit_properties(request, item_id):
    item = shortcuts.get_object_or_404(models.Item, pk=item_id)
    form = forms.ItemUpdatePropertiesForm(instance=item)
    return shortcuts.render(request, 'archive/item_edit_properties.html', {
        'item': item,
        'form': form
    })


@http.require_GET
def item_edit_locations(request, item_id):
    item = shortcuts.get_object_or_404(
        models.Item.objects.prefetch_related(
            'file_locations', 'file_locations__file_object', 'file_locations__file_object__storage',
        ),
        pk=item_id
    )
    return shortcuts.render(request, 'archive/item_edit_locations.html', {
        'item': item,
        'form': forms.ItemUpdateLocationsForm()
    })


@http.require_GET
def item_edit_links(request, item_id):
    item = shortcuts.get_object_or_404(
        models.Item.objects.prefetch_related('includes', 'included_in'),
        pk=item_id
    )
    return shortcuts.render(request, 'archive/item_edit_links.html', {
        'item': item,
    })


@require_ajax
@http.require_POST
def item_update_properties_json(request):
    item_id = request.GET.get('id', None)
    try:
        item = models.Item.objects.get(pk=item_id)
    except models.Item.DoesNotExist:
        return _get_json_item_not_found(item_id)
    except ValueError:
        return _get_json_item_wrong_id(item_id)
    form = forms.ItemUpdatePropertiesForm(request.POST, instance=item)
    if form.is_valid():
        item = form.save()
        models.ItemLog.log_item_update(item, request)
        return JsonWithStatusResponse.ok(urlresolvers.reverse('efsw.archive:item:edit_locations', args=(item.id, )))
    else:
        return JsonWithStatusResponse.error({'errors': form.errors.as_json()})


# ------------------------- ItemCategory -------------------------


@http.require_GET
def category_list(request, page='1'):
    categories = models.ItemCategory.objects.all().order_by('name')
    return shortcuts.render(request, 'archive/category_list.html', {
        'categories': pagination.get_page(categories, page, settings.EFSW_ARCH_CATEGORY_LIST_PER_PAGE),
    })


@http.require_GET
def category_new(request):
    form = forms.ItemCategoryForm()
    return shortcuts.render(request, 'archive/category_new.html', {'form': form})


@require_ajax
@http.require_POST
def category_create_json(request):
    form = forms.ItemCategoryForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonWithStatusResponse.ok(urlresolvers.reverse('efsw.archive:category:list'))
    else:
        return JsonWithStatusResponse.error({'errors': form.errors.as_json()})


@http.require_GET
def category_show_items(request, category_id, page='1'):
    cat = shortcuts.get_object_or_404(models.ItemCategory, pk=category_id)
    items_all = cat.items.all().order_by('-pk')
    items_page = pagination.get_page(items_all, page, settings.EFSW_ARCH_ITEM_LIST_PER_PAGE)
    return shortcuts.render(request, 'archive/category_show_items.html', {
        'items': items_page,
        'category': cat
    })


@http.require_GET
def category_edit(request, category_id):
    cat = shortcuts.get_object_or_404(models.ItemCategory, pk=category_id)
    form = forms.ItemCategoryForm(instance=cat)
    return shortcuts.render(request, 'archive/category_edit.html', {
        'category': cat,
        'form': form
    })


@require_ajax
@http.require_POST
def category_update_json(request):
    cat_id = request.GET.get('id', None)
    try:
        cat = models.ItemCategory.objects.get(pk=cat_id)
    except models.ItemCategory.DoesNotExist:
        return _get_json_category_not_found(cat_id)
    except ValueError:
        return _get_json_category_wrong_id(cat_id)
    form = forms.ItemCategoryForm(request.POST, instance=cat)
    if form.is_valid():
        form.save()
        return JsonWithStatusResponse.ok(urlresolvers.reverse('efsw.archive:category:list'))
    else:
        return JsonWithStatusResponse.error({'errors': form.errors.as_json()})
