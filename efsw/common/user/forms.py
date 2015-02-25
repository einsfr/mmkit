from django import forms


class LoginForm(forms.Form):
    u = forms.CharField(
        max_length=30,
        label='Имя пользователя',
    )
    p = forms.CharField(
        max_length=128,
        label='Пароль',
        widget=forms.PasswordInput,
    )