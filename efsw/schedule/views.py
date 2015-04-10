import datetime

from django import shortcuts
from django.core.exceptions import MultipleObjectsReturned
from django.conf import settings
from django.core import paginator
from django.views.decorators import http
from django.db.models import Count

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


def _get_lineup_table_data(lineup):
    start_times_all_set = set()
    objects_by_day_list = []
    for dow in range(1, 8):
        day_list = list(lineup.program_positions.filter(
            dow=dow,
            start_time__gte=lineup.start_time
        ).order_by('start_time')) + list(lineup.program_positions.filter(
            dow=dow,
            start_time__lt=lineup.start_time
        ).order_by('start_time'))
        objects_by_day_list.append(day_list)
        start_times_all_set = start_times_all_set.union([p.start_time for p in day_list])
    start_times_all_list = sorted(
        filter(lambda x: x >= lineup.start_time, start_times_all_set)
    ) + sorted(
        filter(lambda x: x < lineup.start_time, start_times_all_set)
    )
    by_day_table_data = []
    for dow in range(0, 7):
        day_result = []
        end_time_index = 0
        for pp in objects_by_day_list[dow]:
            if end_time_index:
                start_time_index = end_time_index
            else:
                start_time_index = start_times_all_list.index(pp.start_time)
            if pp.end_time == lineup.end_time:
                end_time_index = len(start_times_all_list)
            else:
                end_time_index = start_times_all_list.index(pp.end_time)
            day_result.append((pp, end_time_index - start_time_index))
        by_day_table_data.append(day_result)
    return by_day_table_data


def _get_lineup_table_data(lineup):
    pp = list(
        lineup.program_positions.filter(start_time__gte=lineup.start_time).order_by('start_time')
    ) + list(
        lineup.program_positions.filter(start_time__lt=lineup.start_time).order_by('start_time')
    )
    start_times_set = set()
    pp_by_day = [[] for _ in range(0, 7)]
    for p in pp:
        start_times_set.add(p.start_time)

    start_times_list = sorted(
        filter(lambda x: x >= lineup.start_time, start_times_set)
    ) + sorted(
        filter(lambda x: x < lineup.start_time, start_times_set)
    )


def lineup_list(request, page=1):
    pass


def lineup_show(lineup_id):
    lineup = shortcuts.get_object_or_404(models.Lineup, pk=lineup_id)
    lineup_table_data = _get_lineup_table_data(lineup)


def lineup_show_current(request):
    lineup = _get_current_lineup()
    if lineup is None:
        return shortcuts.render(request, 'schedule/lineup_show_current.html', {'lineup': None})
    lineup_table_data = _get_lineup_table_data(lineup)
    return shortcuts.render(request, 'schedule/lineup_show_current.html', {
        'lineup': lineup,
        'lineup_table_data': lineup_table_data
    })


def program_list(request, page=1):
    programs = models.Program.objects.all().order_by('name')
    return shortcuts.render(
        request,
        'schedule/program_list.html',
        {
            'programs': _get_program_list_page(programs, page)
        }
    )


@http.require_GET
def program_new(request):
    form = forms.ProgramCreateForm()
    return shortcuts.render(request, 'schedule/program_new.html', {'form': form})


@http.require_POST
def program_create(request):
    form = forms.ProgramCreateForm(request.POST)
    if form.is_valid():
        program = form.save()
        return shortcuts.redirect(program.get_absolute_url())
    else:
        return shortcuts.render(request, 'schedule/program_new.html', {'form': form})


def program_show(request, program_id):
    program = shortcuts.get_object_or_404(
        models.Program,
        pk=program_id
    )
    return shortcuts.render(request, 'schedule/program_show.html', {'program': program})