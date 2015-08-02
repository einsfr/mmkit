from django import forms
from django.forms import widgets

from efsw.conversion import models
from efsw.common.models import FileStorage


class TaskCreateForm(forms.Form):

    name = forms.CharField(
        min_length=3,
        max_length=255,
        label='Название',
        required=False,
        widget=widgets.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Название для задания (необязательно)'
        })
    )

    profile = forms.ModelChoiceField(
        queryset=models.ConversionProfile.objects.all().order_by('name'),
        label='Профиль',
        widget=widgets.Select(attrs={
            'class': 'form-control',
        })
    )


class IOLocationForm(forms.Form):

    path = forms.CharField(
        label='Путь',
        widget=widgets.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Путь в хранилище'
        })
    )


class InputLocationForm(IOLocationForm):

    storage = forms.ModelChoiceField(
        queryset=FileStorage.objects.filter(allowed_usage__contains=['conversion_in']).order_by('name'),
        label='Хранилище',
        widget=widgets.Select(attrs={
            'class': 'form-control',
        })
    )


class OutputLocationForm(IOLocationForm):

    storage = forms.ModelChoiceField(
        queryset=FileStorage.objects.filter(
            allowed_usage__contains=['conversion_out'], read_only=False
        ).order_by('name'),
        label='Хранилище',
        widget=widgets.Select(attrs={
            'class': 'form-control',
        })
    )
