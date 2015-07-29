from django import shortcuts


def home_page(request):
    return shortcuts.render(request, 'common/home/home.html')
