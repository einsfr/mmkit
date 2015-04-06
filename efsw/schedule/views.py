import datetime

from django import shortcuts
from django.core.exceptions import MultipleObjectsReturned
from django.conf import settings
from django.core import paginator

from efsw.schedule import models
from efsw.schedule import default_settings as schedule_default_settings
from efsw.schedule import forms


def _get_current_lineup():
    try:
        lineup = models.Lineup.objects.get(active=True, active_since__lte=datetime.date.today())
    except models.Lineup.DoesNotExist:
        lineup = None
    except MultipleObjectsReturned:
        pass  # TODO: здесь нужно будет снять флажок "активная" со всех лишних сеток, чтобы не делать этого в фоновых процессах
    return lineup


def _get_program_list_page(query_set, page):
    per_page = getattr(
        settings,
        'EFSW_SCHED_PROGRAM_LIST_PER_PAGE',
        schedule_default_settings.EFSW_SCHED_PROGRAM_LIST_PER_PAGE
    )
    paginator_instance = paginator.Paginator(query_set, per_page)
    try:
        programs_page = paginator_instance.page(page)
    except paginator.PageNotAnInteger:
        programs_page = paginator_instance.page(1)
    except paginator.EmptyPage:
        programs_page = paginator_instance.page(paginator_instance.num_pages)
    return programs_page


def lineup_list(request, page=1):
    pass


def lineup_current(request):
    lineup = _get_current_lineup()
    return shortcuts.render(request, 'schedule/lineup_current.html', {'lineup': lineup})


def program_list(request, page=1):
    programs = models.Program.objects.all().order_by('name')
    return shortcuts.render(
        request,
        'schedule/program_list.html',
        {
            'programs': _get_program_list_page(programs, page)
        }
    )


def program_add(request):
    if request.method == 'POST':
        form = forms.ProgramCreateForm(request.POST)
        if form.is_valid():
            program = form.save()
            return shortcuts.redirect(program.get_absolute_url())
    else:
        form = forms.ProgramCreateForm()
    return shortcuts.render(
        request,
        'schedule/program_form_create.html',
        {
            'form': form
        }
    )


def program_detail(request, program_id):
    program = shortcuts.get_object_or_404(
        models.Program,
        pk=program_id
    )
    return shortcuts.render(
        request,
        'schedule/program_detail.html',
        {
            'program': program
        }
    )