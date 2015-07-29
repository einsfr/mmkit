from django.conf.urls import include, url

nav_patterns = [

]

urlpatterns = [
    url(r'^nav/', include((nav_patterns, 'nav', 'nav')))
]
