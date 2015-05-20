from django import forms
from django.forms import widgets

from efsw.archive import models

from efsw.common.datetime.period import DatePeriod


class ItemCreateForm(forms.ModelForm):
    class Meta:
        model = models.Item
        fields = ('name', 'description', 'created', 'author', 'category')
        widgets = {
            'name': widgets.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название нового элемента'
            }),
            'created': widgets.DateInput(attrs={
                'class': 'form-control',
                'placeholder': '01.01.2015'
            }),
            'description': widgets.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание нового элемента',
                'style': 'resize: vertical;'
            }),
            'author': widgets.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Автор(ы) элемента'
            }),
            'category': widgets.Select(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = None


class ItemUpdateForm(forms.ModelForm):
    class Meta(ItemCreateForm.Meta):
        fields = ('name', 'description', 'created', 'author', 'category')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = None


class ItemUpdateAddStorageForm(forms.ModelForm):
    class Meta:
        model = models.ItemLocation
        fields = ('storage', 'location')
        widgets = {
            'storage': widgets.Select(attrs={
                'data-bind': 'value: storage_id, event: { change: storage_changed }',
            }),
            'location': widgets.TextInput(attrs={
                'data-bind': 'value: location, disable: selected_storage().disable_location'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['storage'].empty_label = None


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
        label='Текст запроса',
        required=False,
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
        choices=[('', '---------')] + [(x[0], str(x[1]).capitalize()) for x in DATE_CHOICES.items()],
        label='Дата записи',
        required=False,
    )