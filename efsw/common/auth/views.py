from django import shortcuts
from django.contrib import auth
from django.http import HttpResponseRedirect

from efsw.common.auth import forms


def login(request):
    if request.method == 'GET':
        return shortcuts.render(request, 'common/auth/login.html', {'form': forms.LoginForm()})
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
                        return HttpResponseRedirect('/')
                else:
                    pass
            else:
                pass
        else:
            return shortcuts.render(request, 'common/auth/login.html', {'form': form})


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')