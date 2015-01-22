from django.views import generic

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
