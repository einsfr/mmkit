from django import forms
from django.forms import widgets
from django.contrib.auth.models import User


class UserModelMultipleChoiceField(forms.ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        if obj.first_name and obj.last_name:
            return '{0} {1}'.format(obj.first_name, obj.last_name)
        elif obj.first_name:
            return obj.first_name
        elif obj.last_name:
            return obj.last_name
        else:
            return obj.username


class MessageCreateForm(forms.Form):

    content = forms.CharField(
        label='текст сообщения',
        required=True,
        widget=widgets.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'style': 'resize: vertical;'
        })
    )

    receiver = UserModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('first_name', 'last_name'),
        label='получатели',
        required=True,
        widget=widgets.SelectMultiple(attrs={
            'class': 'form-control',
            'size': 5
        }),
    )

    important = forms.BooleanField(
        label='важное',
        required=False,
    )
