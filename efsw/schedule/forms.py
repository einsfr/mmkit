from django import forms

from efsw.schedule import models


class ProgramCreateForm(forms.ModelForm):

    class Meta:
        model = models.Program
        fields = ('name', 'description', 'age_limit', 'lineup_size', 'max_duration', 'min_duration')


class ProgramPositionControlForm(forms.Form):

    st_h = forms.IntegerField(
        label='Время начала (часы)',
        min_value=0,
        max_value=23
    )

    st_m = forms.IntegerField(
        label='Время начала (минуты)',
        min_value=0,
        max_value=59
    )

    et_h = forms.IntegerField(
        label='Время окончания (часы)',
        min_value=0,
        max_value=23
    )

    et_m = forms.IntegerField(
        label='Время окончания (минуты)',
        min_value=0,
        max_value=59
    )

    c = forms.CharField(
        max_length=32,
        label='Комментарий',
        required=False
    )

    l = forms.BooleanField(
        label='Заблокировано'
    )

    p = forms.ModelChoiceField(
        label='Программа',
        queryset=models.Program.objects.all().order_by('name')
    )