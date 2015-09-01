from django import forms
from django.forms import widgets
from django.forms.formsets import BaseFormSet

from efsw.conversion import models
from efsw.common.models import FileStorage
from efsw.common.storage import errors


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
            'data-bind': 'event: { change: profile_changed }',
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
        empty_label=None,
        widget=widgets.Select(attrs={
            'class': 'form-control',
        })
    )

    def clean(self):
        if self.errors:
            return
        storage = self.cleaned_data['storage']
        path = self.cleaned_data['path']
        if not storage.contains(path):
            self.add_error('path', errors.FILE_DOES_NOT_EXIST_IN_STORAGE.format(storage.name, path))


class OutputLocationForm(IOLocationForm):

    storage = forms.ModelChoiceField(
        queryset=FileStorage.objects.filter(
            allowed_usage__contains=['conversion_out'], read_only=False
        ).order_by('name'),
        label='Хранилище',
        empty_label=None,
        widget=widgets.Select(attrs={
            'class': 'form-control',
        })
    )

    def clean(self):
        if self.errors:
            return
        storage = self.cleaned_data['storage']
        path = self.cleaned_data['path']
        if not storage.contains(path, False):
            self.add_error('path', errors.STORAGE_DOES_NOT_CONTAIN_FILE.format(path, storage.name))
        if storage.contains(path):
            self.add_error('path', errors.FILE_ALREADY_EXISTS_IN_STORAGE.format(path, storage.name))


class BaseInputLocationFormSet(BaseFormSet):
    pass


class BaseOutputLocationFormSet(BaseFormSet):
    pass
