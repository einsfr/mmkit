from django.views import generic
from django import shortcuts
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.core import urlresolvers
from django.core import paginator
from django.views.decorators import http
from django.conf import settings

from efsw.archive import models
from efsw.archive import forms
from efsw.archive import default_settings


def _get_item_index_page(items, page):
    pagin = paginator.Paginator(
        items,
        getattr(settings, 'EFSW_ARCH_INDEX_ITEM_PER_PAGE', default_settings.EFSW_ARCH_INDEX_ITEM_PER_PAGE)
    )
    try:
        items_page = pagin.page(page)
    except paginator.PageNotAnInteger:
        # Если параметр page не является целым числом - показать первую страницу
        items_page = pagin.page(1)
    except paginator.EmptyPage:
        # Если указанная страница - пустая (т.е. находится вне диапазона страниц) - показать последнюю страницу
        items_page = pagin.page(pagin.num_pages)

    return items_page


def item_index(request, page='1'):
    items_all = models.Item.objects.all().order_by('-pk')
    items_page = _get_item_index_page(items_all, page)

    return shortcuts.render(request, 'archive/item_list.html', {'items': items_page})


def item_index_category(request, category='0', page='1'):
    try:
        category_id = int(category)
    except ValueError:
        category_id = 0
    if category_id == 0:
        return item_index(request, page)
    cat = shortcuts.get_object_or_404(models.ItemCategory, pk=category_id)
    items_all = models.Item.objects.filter(category_id=category_id).order_by('-pk')
    items_page = _get_item_index_page(items_all, page)

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


def item_update_remove_link(request, item_id, remove_id):
    item = shortcuts.get_object_or_404(models.Item, pk=item_id)
    item_remove = shortcuts.get_object_or_404(models.Item, pk=remove_id)
    item.includes.remove(item_remove)
    if request.is_ajax():
        return HttpResponse('{0}-{1}'.format(item_id, remove_id))
    else:
        return HttpResponseRedirect(urlresolvers.reverse('efsw.archive:item_detail', args=(item_id, )))


@http.require_http_methods(["POST"])
def item_update_add_link(request, item_id):
    item = shortcuts.get_object_or_404(models.Item, pk=item_id)
    form = forms.ItemUpdateAddLinkForm(request.POST)
    if form.is_valid():
        linked_id = form.cleaned_data['linked_id']
        try:
            linked_item = models.Item.objects.get(pk=linked_id)
        except models.Item.DoesNotExist:
            linked_item = None
        if linked_item is None:
            if request.is_ajax():
                return HttpResponseBadRequest()
            else:
                return HttpResponseRedirect(urlresolvers.reverse('efsw.archive:item_detail', args=(item_id, )))
        item.includes.add(linked_item)
        if request.is_ajax():
            return shortcuts.render(request, 'archive/item_detail_link.html', {'object': item, 'item': linked_item})
        else:
            return HttpResponseRedirect(urlresolvers.reverse('efsw.archive:item_detail', args=(item_id, )))
    else:
        if request.is_ajax():
            return HttpResponseBadRequest()
        else:
            return HttpResponseRedirect(urlresolvers.reverse('efsw.archive:item_detail', args=(item_id, )))


class CategoryIndexView(generic.ListView):
    queryset = models.ItemCategory.objects.all().order_by('name')
    template_name = 'archive/category_list.html'


class CategoryAddView(generic.CreateView):
    pass