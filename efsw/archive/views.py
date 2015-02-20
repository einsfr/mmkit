import json

from django.views import generic
from django import shortcuts
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.core import paginator
from django.views.decorators import http
from django.conf import settings
from django.core import urlresolvers
from django.template import loader
from django.views.decorators import csrf

from efsw.archive import models
from efsw.archive import forms
from efsw.archive import default_settings as archive_default_settings
from efsw.common import default_settings as common_default_settings
from efsw.common.search import elastic


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
    items_all = models.Item.objects.all().order_by('-pk')
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
    items_all = models.Item.objects.filter(category_id=category_id).order_by('-pk')
    items_page = _get_item_list_page(items_all, page)

    return shortcuts.render(request, 'archive/item_list_category.html', {'items': items_page, 'category': cat})


class ItemDetailView(generic.DetailView):
    model = models.Item

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        context['link_add_form'] = forms.ItemUpdateAddLinkForm()

        return context


class ItemAddView(generic.CreateView):
    model = models.Item
    template_name = 'archive/item_form_create.html'
    form_class = forms.ItemCreateForm


class ItemUpdateView(generic.UpdateView):
    model = models.Item
    template_name = 'archive/item_form_update.html'
    form_class = forms.ItemUpdateForm


class ItemUpdateStorageView(generic.UpdateView):
    model = models.Item
    template_name = 'archive/item_form_update_storage.html'
    form_class = forms.ItemUpdateStorageForm


@http.require_http_methods(["POST"])
def item_update_remove_link(request, item_id):
    item = shortcuts.get_object_or_404(models.Item, pk=item_id)
    form = forms.ItemUpdateRemoveLinkForm(request.POST)
    if form.is_valid():
        removed_id = form.cleaned_data['removed_id']
        try:
            removed_item = models.Item.objects.get(pk=removed_id)
            item.includes.remove(removed_item)
        except models.Item.DoesNotExist:
            pass  # @TODO Здесь по-хорошему надо вносить в лог попытку удалить несуществующий элемент
        return HttpResponse('{0}-{1}'.format(item_id, removed_id))
    else:
        return HttpResponseBadRequest()


@http.require_http_methods(["POST"])
def item_update_add_link(request, item_id):
    item = shortcuts.get_object_or_404(models.Item, pk=item_id)
    form = forms.ItemUpdateAddLinkForm(request.POST)
    if form.is_valid():
        linked_id = form.cleaned_data['linked_id']
        try:
            linked_item = models.Item.objects.get(pk=linked_id)
        except models.Item.DoesNotExist:
            return HttpResponseBadRequest()
        item.includes.add(linked_item)
        return shortcuts.render(request, 'archive/_item_detail_link.html', {'object': item, 'item': linked_item})
    else:
        return HttpResponseBadRequest()


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
    es = elastic.get_es()
    es_status = elastic.get_es_status()
    if es is None or (es_status != 'yellow' and es_status != 'green'):
        return HttpResponseServerError(loader.render_to_string('archive/search_offline.html'))

    if not request.GET.get('q'):
        return shortcuts.render(request, 'archive/search.html', {'form': forms.ArchiveSearchForm})

    form = forms.ArchiveSearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['q']
        # TODO: Всё это должно происходить в отдельном классе - каком-нибудь QueryBuilder'е
        query_body = {
            'query': {
                'filtered': {
                    'query': {
                        'multi_match': {
                            'query': str(query),
                            'fields': ['name', 'description', 'author']
                        }
                    }
                }
            }
        }
        order = form.cleaned_data['o']
        if order == forms.ArchiveSearchForm.ORDER_BY_CREATED_ASC:
            query_body['sort'] = [{'created': 'asc'}]
        elif order == forms.ArchiveSearchForm.ORDER_BY_CREATED_DESC:
            query_body['sort'] = [{'created': 'desc'}]
        else:
            query_body['sort'] = []
        query_body['sort'].append('_score')
        categories = form.cleaned_data['c']
        if categories:
            query_body['query']['filtered']['filter'] = {
                'terms': {'category': [x.id for x in categories]}
            }
        else:
            query_body['query']['filtered']['filter'] = {
                'match_all': {}
            }
        search_size = getattr(
            settings,
            'EFSW_ELASTIC_MAX_SEARCH_RESULTS',
            common_default_settings.EFSW_ELASTIC_MAX_SEARCH_RESULTS
        )
        result = es.search(index='efswarchitem', doc_type='item', body=json.dumps(query_body), size=search_size)
        hits = result['hits']
        if hits['total']:
            hits_ids = [h['_id'] for h in hits['hits']]
            items_dict = dict(
                map(lambda x: (str(x.id), x), models.Item.objects.filter(id__in=hits_ids))
            )
            items = filter(lambda x: x is not None, [items_dict.get(x) for x in hits_ids])
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