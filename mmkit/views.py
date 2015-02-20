from django import shortcuts


def home_page(request):
    return shortcuts.render(request, 'home.html')