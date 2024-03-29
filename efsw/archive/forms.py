from django import forms
from django.forms import widgets

from efsw.archive import models
from efsw.storage import models as storage_models

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


class ItemUpdatePropertiesForm(forms.ModelForm):
    class Meta(ItemCreateForm.Meta):
        fields = ('name', 'description', 'created', 'author', 'category')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = None


class ItemUpdateLocationsForm(forms.Form):

    storage = forms.ModelChoiceField(
        queryset=storage_models.FileStorage.objects.filter(allowed_usage__contains=['archive']),
        label='Хранилище',
        empty_label=None,
        widget=widgets.Select(attrs={
            'class': 'form-control',
            'data-bind': 'value: form_storage',
        })
    )

    path = forms.CharField(
        max_length=255,
        label='Путь к файлу',
        widget=widgets.TextInput(attrs={
            'class': 'form-control',
            'data-bind': 'textInput: form_path',
        })
    )


class ItemCategoryForm(forms.ModelForm):
    class Meta:
        model = models.ItemCategory
        fields = ('name', )
        widgets = {
            'name': widgets.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название новой категории'
            })
        }


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
        widget=widgets.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Текст поискового запроса'
        })
    )
    c = forms.ModelMultipleChoiceField(
        queryset=models.ItemCategory.objects.all().order_by('name'),
        label='Категория',
        required=False,
        widget=widgets.SelectMultiple(attrs={
            'class': 'form-control',
        })
    )
    o = forms.ChoiceField(
        choices=[('', 'По релевантности')] + list(ORDER_CHOICES.items()),
        label='Порядок сортировки',
        required=False,
        widget=widgets.Select(attrs={
            'class': 'form-control',
        })
    )
    p = forms.ChoiceField(
        choices=[('', 'За всё время')] +
                [(x[0], str(x[1]).capitalize()) for x in DATE_CHOICES.items()] +
                [('custom', 'Указать особый')],
        label='Дата записи',
        required=False,
        widget=widgets.Select(attrs={
            'class': 'form-control',
            'data-bind': 'value: selected_period'
        })
    )
    p_s = forms.DateField(
        required=False,
        label='Начало периода',
        widget=widgets.DateInput(attrs={
            'class': 'form-control',
            'placeholder': '01.01.2015'
        }),
    )
    p_e = forms.DateField(
        required=False,
        label='Конец периода',
        widget=widgets.DateInput(attrs={
            'class': 'form-control',
            'placeholder': '01.01.2015'
        }),
    )
    ph = forms.BooleanField(
        required=False,
        label='Искать фразу'
    )
