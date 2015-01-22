from django.views import generic
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core import urlresolvers

from efsw.archive import models
from efsw.archive import forms


class IndexView(generic.ListView):
    queryset = models.Item.objects.order_by('-pk')


class DetailView(generic.DetailView):
    model = models.Item


class ItemCreateView(generic.CreateView):
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
    item = get_object_or_404(models.Item, pk=item_id)
    item_remove = get_object_or_404(models.Item, pk=remove_id)
    item.includes.remove(item_remove)
    if request.is_ajax():
        return HttpResponse()
    else:
        return HttpResponseRedirect(urlresolvers.reverse('efsw.archive:item_detail', args=(item_id, )))
