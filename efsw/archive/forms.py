from django.forms import ModelForm

from efsw.archive import models


class ItemCreateForm(ModelForm):
    class Meta:
        model = models.Item
        fields = ('name', 'description', 'created', 'author', 'storage', 'category')


class ItemUpdateForm(ItemCreateForm):
    class Meta(ItemCreateForm.Meta):
        exclude = ('storage', )


class ItemUpdateStorageForm(ModelForm):
    class Meta:
        model = models.Item
        fields = ('storage', )