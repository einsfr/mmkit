from django import forms

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
                'placeholder': '00:00'
            }),
            'end_time': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00:00'
            }),
            'channel': forms.Select(attrs={
                'class': 'form-control',
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['channel'].queryset = self.fields['channel'].queryset.exclude(active=False)
        self.fields['channel'].empty_label = None


class ProgramCreateForm(forms.ModelForm):

    class Meta:
        model = models.Program
        fields = ('name', 'description', 'age_limit', 'lineup_size', 'max_duration', 'min_duration')


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
        })
    )

    st_m = forms.IntegerField(
        label='Время начала (минуты)',
        min_value=0,
        max_value=59,
        widget=forms.NumberInput(attrs={
            'data-bind': 'value: pp().start_minutes',
        })
    )

    et_h = forms.IntegerField(
        label='Время окончания (часы)',
        min_value=0,
        max_value=23,
        widget=forms.NumberInput(attrs={
            'data-bind': 'value: pp().end_hours',
        })
    )

    et_m = forms.IntegerField(
        label='Время окончания (минуты)',
        min_value=0,
        max_value=59,
        widget=forms.NumberInput(attrs={
            'data-bind': 'value: pp().end_minutes',
        })
    )

    c = forms.CharField(
        max_length=32,
        label='Комментарий',
        required=False,
        widget=forms.TextInput(attrs={
            'data-bind': 'value: pp().comment',
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
        })
    )