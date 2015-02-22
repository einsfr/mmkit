from django import forms

from efsw.archive import models

from efsw.common.datetime.period import DatePeriod

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
    ORDER_BY_CREATED_ASC = '1'
    ORDER_BY_CREATED_DESC = '2'

    ORDER_CHOICES = {
        ORDER_BY_CREATED_ASC: 'По дате создания (по возрастанию)',
        ORDER_BY_CREATED_DESC: 'По дате создания (по убыванию)',
    }

    DATE_PERIODS = DatePeriod.PERIODS_PAST_ONLY_WITH_TODAY

    DATE_CHOICES = DatePeriod.get_periods_past_only()

    q = forms.CharField(
        min_length=3,
        max_length=255,
        label='Текст запроса'
    )
    c = forms.ModelMultipleChoiceField(
        queryset=models.ItemCategory.objects.all().order_by('name'),
        label='Категория',
        required=False,
    )
    o = forms.ChoiceField(
        choices=[('', 'По релевантности')] + list(ORDER_CHOICES.items()),
        label='Порядок сортировки',
        required=False,
    )
    p = forms.ChoiceField(
        choices=[(x[0], str(x[1]).capitalize()) for x in DATE_CHOICES.items()],
        label='Дата записи',
        required=False,
    )