from django.views import generic
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.core import urlresolvers
from django.views.decorators import http

from efsw.archive import models
from efsw.archive import forms


class IndexView(generic.ListView):
    queryset = models.Item.objects.order_by('-pk')


class DetailView(generic.DetailView):
    model = models.Item

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['link_add_form'] = forms.ItemUpdateAddLinkForm()
        return context


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
        return HttpResponse('{0}-{1}'.format(item_id, remove_id))
    else:
        return HttpResponseRedirect(urlresolvers.reverse('efsw.archive:item_detail', args=(item_id, )))


@http.require_http_methods(["POST"])
def item_update_add_link(request, item_id):
    item = get_object_or_404(models.Item, pk=item_id)
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
            return render(request, 'archive/item_detail_link.html', {'object': item, 'item': linked_item})
        else:
            return HttpResponseRedirect(urlresolvers.reverse('efsw.archive:item_detail', args=(item_id, )))
    else:
        if request.is_ajax():
            return HttpResponseBadRequest()
        else:
            return HttpResponseRedirect(urlresolvers.reverse('efsw.archive:item_detail', args=(item_id, )))