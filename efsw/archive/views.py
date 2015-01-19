from django.views import generic

from efsw.archive import models


class IndexView(generic.ListView):
    queryset = models.Item.objects.order_by('-pk')


class DetailView(generic.DetailView):
    model = models.Item


class CreateView(generic.CreateView):
    model = models.Item
    fields = ['name', 'description', 'created', 'author', 'storage', 'category']


class UpdateView(generic.UpdateView):
    model = models.Item
    fields = ['name', 'description', 'created', 'author', 'category']


class UpdateStorageView(generic.UpdateView):
    pass


class UpdateLinkView(generic.UpdateView):
    pass