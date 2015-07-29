from django.conf.urls import include, url

urlpatterns = [
    url(r'^accounts/', include('efsw.common.accounts.urls', namespace='efsw.common.accounts')),
]
