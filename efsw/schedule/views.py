from django import shortcuts


def lineup_current(request):
    return shortcuts.render(request, 'schedule/lineup_current.html')