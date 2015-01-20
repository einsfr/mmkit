from django.views import generic

from efsw.archive import models
from efsw.archive import forms


class IndexView(generic.ListView):
    queryset = models.Item.objects.order_by('-pk')


class DetailView(generic.DetailView):
    model = models.Item


class CreateView(generic.FormView):
    template_name = 'archive/item_form.html'
    form_class = forms.ItemCreateForm


class UpdateView(generic.FormView):
    template_name = 'archive/item_form.html'
    form_class = forms.ItemUpdateForm


class UpdateStorageView(generic.UpdateView):
    pass


class UpdateLinkView(generic.UpdateView):
    pass