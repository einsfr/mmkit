from django.conf.urls import include, url

from efsw.storage import views

nav_patterns = [
    # nav/ls/json/?s=1ac9873a-8cf0-49e1-8a9a-7709930aa8af&p=test&d=1
    # Тесты:
    url(
        r'^ls/json/$',
        views.nav_ls_json,
        name='nav_ls_json'
    )
]

urlpatterns = [
    url(r'^nav/', include((nav_patterns, 'nav', 'nav')))
]
