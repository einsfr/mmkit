from django import forms
from django.forms import widgets

from efsw.conversion import models


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
