import datetime

from django import forms
from django.core.exceptions import ValidationError

from efsw.schedule import models


class LineupCreateForm(forms.ModelForm):

    class Meta:
        model = models.Lineup
        fields = ('name', 'start_time', 'end_time', 'channel')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название сетки вещания'
            }),
            'start_time': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например, 00:00'
            }),
            'end_time': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например, 00:00'
            }),
            'channel': forms.Select(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['channel'].queryset = self.fields['channel'].queryset.exclude(active=False)
        self.fields['channel'].empty_label = None


class LineupUpdateForm(forms.ModelForm):

    class Meta:
        model = models.Lineup
        fields = ('name', )
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            })
        }


class LineupCopyForm(forms.ModelForm):

    class Meta:
        model = models.Lineup
        fields = ('name', )
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название для копии',
            })
        }


class LineupActivateForm(forms.ModelForm):

    class Meta:
        model = models.Lineup
        fields = ('active_since', )
        widgets = {
            'active_since': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например, 01.01.2015'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['active_since'].required = True

    def clean_active_since(self):
        if self.cleaned_data['active_since'] <= datetime.date.today():
            raise ValidationError('Дата активации не может быть меньше или равна текущей дате.')
        return self.cleaned_data['active_since']


class ProgramCreateForm(forms.ModelForm):

    class Meta:
        model = models.Program
        fields = ('name', 'description', 'age_limit', 'lineup_size', 'max_duration', 'min_duration', 'color')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название для новой программы'
            }),
            'lineup_size': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например, 00:30:00'
            }),
            'max_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например, 00:26:00'
            }),
            'min_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например, 00:21:00'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание новой программы',
                'style': 'resize: vertical;'
            }),
            'age_limit': forms.Select(attrs={
                'class': 'form-control'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'data-bind': 'event: { change: color_changed }'
            })
        }


class ProgramPositionRepeatForm(forms.Form):

    r = forms.MultipleChoiceField(
        choices=models.ProgramPosition.DOW_DICT.items(),
        label='Повторить для',
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )


class ProgramPositionEditForm(ProgramPositionRepeatForm):

    st_h = forms.IntegerField(
        label='Время начала (часы)',
        min_value=0,
        max_value=23,
        widget=forms.NumberInput(attrs={
            'data-bind': 'value: pp().start_hours',
            'class': 'form-control'
        })
    )

    st_m = forms.IntegerField(
        label='Время начала (минуты)',
        min_value=0,
        max_value=59,
        widget=forms.NumberInput(attrs={
            'data-bind': 'value: pp().start_minutes',
            'class': 'form-control'
        })
    )

    et_h = forms.IntegerField(
        label='Время окончания (часы)',
        min_value=0,
        max_value=23,
        widget=forms.NumberInput(attrs={
            'data-bind': 'value: pp().end_hours',
            'class': 'form-control'
        })
    )

    et_m = forms.IntegerField(
        label='Время окончания (минуты)',
        min_value=0,
        max_value=59,
        widget=forms.NumberInput(attrs={
            'data-bind': 'value: pp().end_minutes',
            'class': 'form-control'
        })
    )

    c = forms.CharField(
        max_length=32,
        label='Комментарий',
        required=False,
        widget=forms.TextInput(attrs={
            'data-bind': 'value: pp().comment',
            'class': 'form-control'
        })
    )

    l = forms.BooleanField(
        label='Заблокировано',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'data-bind': 'checked: pp().locked',
        })
    )

    p = forms.ModelChoiceField(
        label='Программа',
        queryset=models.Program.objects.all().order_by('name'),
        required=False,
        widget=forms.Select(attrs={
            'data-bind': 'value: pp().program_id, event: { change: program_changed }',
            'class': 'form-control'
        })
    )