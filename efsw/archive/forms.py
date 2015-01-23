from django import forms

from efsw.archive import models


class ItemCreateForm(forms.ModelForm):
    class Meta:
        model = models.Item
        fields = ('name', 'description', 'created', 'author', 'storage', 'category')


class ItemUpdateForm(ItemCreateForm):
    class Meta(ItemCreateForm.Meta):
        exclude = ('storage', )


class ItemUpdateStorageForm(forms.ModelForm):
    class Meta:
        model = models.Item
        fields = ('storage', )


class ItemUpdateAddLinkForm(forms.Form):
    linked_id = forms.IntegerField(min_value=1, label='Связанный ID')