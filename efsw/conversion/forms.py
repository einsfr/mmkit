from django import forms
from django.forms import widgets
from django.forms.formsets import BaseFormSet
from django.core.exceptions import ValidationError

from efsw.conversion import models
from efsw.storage.models import FileStorage
from efsw.storage import errors


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


class ProfileCreateForm(forms.Form):

    name = forms.CharField(
        min_length=3,
        max_length=255,
        label='Название',
        required=True,
        widget=widgets.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Название для профиля'
        })
    )

    description = forms.CharField(
        label='Описание',
        required=False,
        widget=widgets.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Описание профиля (необязательно)',
            'rows': 3,
            'style': 'resize: vertical;',
        })
    )

    global_options = forms.CharField(
        label='Глобальные опции',
        required=False,
        widget=widgets.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Глобальные опции конвертера (необязательно)',
            'rows': 2,
            'style': 'resize: vertical;',
        })
    )

    def clean_name(self):
        if models.ConversionProfile.objects.filter(name=self.cleaned_data['name']).exists():
            raise ValidationError('Название профиля должно быть уникальным.')
        return self.cleaned_data['name']


class IOForm(forms.Form):

    comment = forms.CharField(
        max_length=255,
        label='Комментарий',
        required=False,
        widget=widgets.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Комментарий (необязательно)'
        })
    )

    allowed_ext = forms.CharField(
        max_length=255,
        label='Допустимые расширения файлов',
        required=False,
        widget=widgets.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Допустимые расширеня файлов (через пробел, необязательно)'
        })
    )

    options = forms.CharField(
        label='Опции',
        required=False,
        widget=widgets.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Опции (необязательно)',
            'style': 'resize: vertical;',
            'rows': 2
        })
    )


class BaseIOFormSet(BaseFormSet):
    pass
