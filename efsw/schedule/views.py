import datetime

from django import shortcuts
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.conf import settings
from django.core import paginator
from django.views.decorators import http

from efsw.schedule import models
from efsw.schedule import default_settings as schedule_default_settings
from efsw.schedule import forms
from efsw.common.http.response import JsonWithStatusResponse


def _get_current_lineup(channel):
    try:
        lineup = models.Lineup.objects.get(active=True, channel=channel, active_since__lte=datetime.date.today())  # TODO условие надо будет подправить
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
    pp = list(
        lineup.program_positions.filter(start_time__gte=lineup.start_time).select_related('program')
    ) + list(
        lineup.program_positions.filter(start_time__lt=lineup.start_time).select_related('program')
    )
    start_times_set = set()
    pp_by_day = [dict() for _ in range(0, 7)]
    for p in pp:
        start_times_set.add(p.start_time)
        pp_by_day[p.dow - 1][p.start_time] = p
    start_times_list = sorted(
        filter(lambda x: x >= lineup.start_time, start_times_set)
    ) + sorted(
        filter(lambda x: x < lineup.start_time, start_times_set)
    )
    result = []
    start_times_count = len(start_times_list)
    for start_time_index, st in enumerate(start_times_list):
        row = [st]
        for dow in range(0, 7):
            if st in pp_by_day[dow]:
                p = pp_by_day[dow][st]
                if p.end_time == lineup.end_time:
                    end_time_index = start_times_count
                else:
                    end_time_index = start_times_list.index(p.end_time)
                row.append({'pp': p, 'row_span': end_time_index - start_time_index})
        result.append(row)
    return result


def lineup_list(request, page=1):
    pass


def lineup_show(lineup_id):
    lineup = shortcuts.get_object_or_404(models.Lineup, pk=lineup_id)
    lineup_table_data = _get_lineup_table_data(lineup)


def lineup_show_current(request):
    lineup = _get_current_lineup(models.Channel.objects.get(pk=1))
    if lineup is None:
        return shortcuts.render(request, 'schedule/lineup_show_current.html', {'lineup': None})
    lineup_table_data = _get_lineup_table_data(lineup)
    return shortcuts.render(request, 'schedule/lineup_show_current.html', {
        'lineup': lineup,
        'lineup_table_data': lineup_table_data,
        'pp_control_form': forms.ProgramPositionControlForm()
    })


def lineup_show_part_pp_table_body(request, lineup_id):
    lineup = shortcuts.get_object_or_404(models.Lineup, pk=lineup_id)
    return shortcuts.render(request, 'schedule/_pp_list_table_body.html', {
        'lineup_table_data': _get_lineup_table_data(lineup)
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


def _get_json_program_not_found(program_id):
    return JsonWithStatusResponse(
        'Ошибка: программа с ID "{0}" не найдена'.format(program_id),
        JsonWithStatusResponse.STATUS_ERROR
    )


def program_show_json(request):

    def format_program_dict(p):
        return {
            'name': p.name,
            'ls_hours': p.lineup_size.hour,
            'ls_minutes': p.lineup_size.minute,
            'age_limit': p.format_age_limit()
        }

    program_id = request.GET.get('id', None)
    try:
        program = models.Program.objects.get(pk=program_id)
    except models.Program.DoesNotExist:
        return _get_json_program_not_found(program_id)
    return JsonWithStatusResponse(format_program_dict(program))


def _get_json_pp_not_found(pp_id):
    return JsonWithStatusResponse(
        'Ошибка: не найден фрагмент сетки вещания с ID "{0}"'.format(pp_id),
        JsonWithStatusResponse.STATUS_ERROR
    )


def pp_show_json(request):

    def format_pp_dict(pp):
        return_dict = {
            'id': pp.id,
            'dow': pp.DOW_DICT[pp.dow],
            'start_hours': pp.start_time.hour,
            'start_minutes': pp.start_time.minute,
            'end_hours': pp.end_time.hour,
            'end_minutes': pp.end_time.minute,
            'comment': pp.comment,
            'locked': pp.locked,
            'similar_pps': [x.dow for x in _get_similar(pp)]
        }
        if pp.program:
            return_dict['program_id'] = pp.program.id
        else:
            return_dict['program_id'] = 0
        return return_dict

    pp_id = request.GET.get('id', None)
    try:
        program_position = models.ProgramPosition.objects.select_related('program').get(pk=pp_id)
    except models.ProgramPosition.DoesNotExist:
        return _get_json_pp_not_found(pp_id)
    return JsonWithStatusResponse(format_pp_dict(program_position))


def _get_json_delete_empty_pp(pp_id):
    return JsonWithStatusResponse(
        'Ошибка: невозможно удалить пустой фрагмент с ID "{0}"'.format(pp_id),
        JsonWithStatusResponse.STATUS_ERROR
    )


def _clear_program(pp):
    pp.program = None
    pp.save()


def _expand_next(pp, next_pp):
    next_pp.start_time = pp.start_time
    pp.delete()
    next_pp.save()


def _expand_previous(pp, previous_pp):
    previous_pp.end_time = pp.end_time
    pp.delete()
    previous_pp.save()


def _merge_neighbours(pp, previous_pp, next_pp):
    previous_pp.end_time = next_pp.end_time
    pp.delete()
    next_pp.delete()
    previous_pp.save()


def _pp_is_empty(pp):
    return not pp.program and not pp.comment and not pp.locked


def _pp_delete(program_position):
    lineup = program_position.lineup
    if program_position.start_time == lineup.start_time:
        previous_pp = None
    else:
        previous_pp = lineup.program_positions.get(dow=program_position.dow, end_time=program_position.start_time)
    if program_position.end_time == lineup.end_time:
        next_pp = None
    else:
        next_pp = lineup.program_positions.get(dow=program_position.dow, start_time=program_position.end_time)

    if (previous_pp is not None and _pp_is_empty(previous_pp)) and (next_pp is None or not _pp_is_empty(next_pp)):
        _expand_previous(program_position, previous_pp)
    elif (previous_pp is None or not _pp_is_empty(previous_pp)) and (next_pp is not None and _pp_is_empty(next_pp)):
        _expand_next(program_position, next_pp)
    elif (previous_pp is not None and _pp_is_empty(previous_pp)) and (next_pp is not None and _pp_is_empty(next_pp)):
        _merge_neighbours(program_position, previous_pp, next_pp)
    else:
        _clear_program(program_position)


def _get_similar(program_position):
    return models.ProgramPosition.objects.filter(
        lineup=program_position.lineup,
        start_time=program_position.start_time,
        end_time=program_position.end_time,
        locked=program_position.locked,
        program=program_position.program,
    ).exclude(dow=program_position.dow).select_related('lineup')


def pp_delete_json(request):
    pp_id = request.GET.get('id', None)
    try:
        program_position = models.ProgramPosition.objects.select_related('lineup').get(pk=pp_id)
    except models.ProgramPosition.DoesNotExist:
        return _get_json_pp_not_found(pp_id)
    if not program_position.program:
        return _get_json_delete_empty_pp(pp_id)
    if request.POST.get('r', None) is not None:
        form = forms.ProgramPositionRepeatForm(request.POST)
        if form.is_valid():
            for d in [x for x in _get_similar(program_position) if str(x.dow) in form.cleaned_data.get('r')]:
                _pp_delete(d)
        else:
            return JsonWithStatusResponse(
                'Неправильный формат списка повторов',
                JsonWithStatusResponse.STATUS_ERROR
            )
    _pp_delete(program_position)
    return JsonWithStatusResponse()


def pp_update_json(request):
    pp_id = request.GET.get('id', None)
    try:
        program_position = models.ProgramPosition.objects.select_related('lineup').get(pk=pp_id)
    except models.ProgramPosition.DoesNotExist:
        return _get_json_pp_not_found(pp_id)
    form = forms.ProgramPositionControlForm(request.POST)
    if form.is_valid():
        start_time = datetime.time(form.cleaned_data['st_h'], form.cleaned_data['st_m'])
        end_time = datetime.time(form.cleaned_data['et_h'], form.cleaned_data['et_m'])
        program = form.cleaned_data.get('p', None)
        locked = form.cleaned_data['l']
        comment = form.cleaned_data['c']
        if start_time == program_position.start_time and end_time == program_position.end_time:
            # Если фрагмент не меняет свою длительность
            if program or comment or locked:
                # и при этом становится или остаётся не пустым
                program_position.comment = comment
                program_position.program = program
                program_position.locked = locked
                try:
                    program_position.full_clean()
                except ValidationError as e:
                    return JsonWithStatusResponse.error(e.message_dict)
                program_position.save()
                return JsonWithStatusResponse.ok()
            else:
                # если же становится или остаётся пустым
                _pp_delete(program_position)
                return JsonWithStatusResponse.ok()
        else:
            # А если всё-таки меняет длительность
            pass

    else:
        return JsonWithStatusResponse.error(form.errors.as_json())
