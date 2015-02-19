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


class ItemUpdateRemoveLinkForm(forms.Form):
    removed_id = forms.IntegerField(min_value=1)


class ItemCategoryForm(forms.ModelForm):
    class Meta:
        model = models.ItemCategory
        fields = ('name', )


class ArchiveSearchForm(forms.Form):
    ORDER_BY_CREATED_ASC = 'cra'
    ORDER_BY_CREATED_DESC = 'crd'

    ORDER_CHOICES = {
        ORDER_BY_CREATED_ASC: 'По дате создания (по возрастанию)',
        ORDER_BY_CREATED_DESC: 'По дате создания (по убыванию)',
    }

    q = forms.CharField(
        min_length=3,
        max_length=255,
        label='Текст запроса'
    )
    o = forms.ChoiceField(
        choices=[('', 'По релевантности')] + list(ORDER_CHOICES.items()),
        label='Порядок сортировки',
        required=False,
    )