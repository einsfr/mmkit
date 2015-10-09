from django.conf.urls import include, url

urlpatterns = [
    url(r'^accounts/', include('efsw.common.accounts.urls', namespace='efsw.common.accounts')),
    url(r'^storage/', include('efsw.common.storage.urls', namespace='efsw.common.storage')),
    url(r'^im/', include('efsw.common.im.urls', namespace='efsw.common.im')),
]
