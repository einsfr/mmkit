from django import shortcuts
from django.contrib import auth
from django.http import HttpResponseRedirect

from efsw.common.user import forms


def login(request):
    if request.method == 'GET':
        return shortcuts.render(request, 'common/user/login.html', {'form': forms.LoginForm()})
    elif request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['u']
            password = form.cleaned_data['p']
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    redirect_url = request.GET.get('r')
                    if redirect_url:
                        return HttpResponseRedirect(redirect_url)
                    else:
                        # TODO: Здесь надо будет придумать для пользователей какую-нибудь домашнюю страницу, куда они и будут отправляться, если сами зашли на страничку входа
                        return HttpResponseRedirect('/')
                else:
                    return shortcuts.render(
                        request,
                        'common/user/login.html',
                        {
                            'form': form,
                            'login_error': 'Пользователь с таким именем заблокирован - обратитесь к администратору.'
                        }
                    )
            else:
                return shortcuts.render(
                        request,
                        'common/user/login.html',
                        {
                            'form': form,
                            'login_error': 'Ошибка входа в систему - неправильные имя пользователя или пароль.'
                        }
                    )
        else:
            return shortcuts.render(request, 'common/user/login.html', {'form': form})


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')