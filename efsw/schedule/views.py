import datetime
import json

from django import shortcuts
from django.core.exceptions import ValidationError
from django.conf import settings
from django.views.decorators import http
from django.http import Http404
from django.db.models import Q
from django.core import urlresolvers
from django.contrib.auth.decorators import permission_required

from efsw.schedule import models, forms, errors
from efsw.common.http.response import JsonWithStatusResponse
from efsw.schedule import lineops
from efsw.common.db import pagination
from efsw.common.http.decorators import require_ajax
from efsw.common.utils import params


def _get_current_lineup(channel, date=None):
    if date is None:
        date = datetime.date.today()
    try:
        lineup = models.Lineup.objects.get(
            Q(active_since__lte=date),
            Q(active_until__gte=date) | Q(active_until__isnull=True),
            draft=False,
            channel=channel,
        )
    except models.Lineup.DoesNotExist:
        lineup = None
    return lineup


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
    return {
        'rows': result,
        'lineup_start_time': lineup.start_time,
        'lineup_end_time': lineup.end_time,
    }


def _get_json_lineup_not_found(lineup_id):
    return JsonWithStatusResponse.error(
        'Ошибка: сетка вещания с ID "{0}" не найдена'.format(lineup_id),
        'lineup_not_found'
    )


def _get_json_wrong_lineup_id(lineup_id):
    return JsonWithStatusResponse.error(
        'Ошибка: идентификатор сетки вещания должен быть целым числом, предоставлено: "{0}"'.format(lineup_id),
        'id_not_int'
    )


def _get_json_lineup_edit_forbidden(lineup_id):
    return JsonWithStatusResponse.error(
        'Ошибка: сетка вещания с ID "{0}" закрыта для редактирования'.format(lineup_id),
        'lineup_edit_forbidden'
    )


def _get_json_program_not_found(program_id):
    return JsonWithStatusResponse.error(
        'Ошибка: программа с ID "{0}" не найдена'.format(program_id),
        'program_not_found'
    )


def _get_json_wrong_program_id(program_id):
    return JsonWithStatusResponse.error(
        'Ошибка: идентификатор программы должен быть целым числом, предоставлено: "{0}"'.format(program_id),
        'id_not_int'
    )


def _get_json_pp_not_found(pp_id):
    return JsonWithStatusResponse.error(
        'Ошибка: не найден фрагмент сетки вещания с ID "{0}"'.format(pp_id),
        'pp_not_found'
    )


def _get_json_wrong_pp_id(pp_id):
    return JsonWithStatusResponse.error(
        'Ошибка: идентификатор фрагмента сетки вещания должен быть целым числом, предоставлено: "{0}"'.format(pp_id),
        'id_not_int'
    )


def _get_json_delete_empty_pp(pp_id):
    return JsonWithStatusResponse.error(
        'Ошибка: невозможно удалить пустой фрагмент с ID "{0}"'.format(pp_id),
        'pp_delete_empty'
    )


def _pp_delete(program_position):
    previous_pp = lineops.get_previous_pp(program_position)
    next_pp = lineops.get_next_pp(program_position)
    if (previous_pp is not None and lineops.pp_is_empty(previous_pp)) \
            and (next_pp is None or not lineops.pp_is_empty(next_pp)):
        previous_pp.end_time = program_position.end_time
        program_position.delete()
        previous_pp.save()
    elif (previous_pp is None or not lineops.pp_is_empty(previous_pp)) \
            and (next_pp is not None and lineops.pp_is_empty(next_pp)):
        next_pp.start_time = program_position.start_time
        program_position.delete()
        next_pp.save()
    elif (previous_pp is not None and lineops.pp_is_empty(previous_pp)) \
            and (next_pp is not None and lineops.pp_is_empty(next_pp)):
        previous_pp.end_time = next_pp.end_time
        program_position.delete()
        next_pp.delete()
        previous_pp.save()
    else:
        program_position.program = None
        program_position.save()


def _get_json_channel_not_found(channel_id):
    return JsonWithStatusResponse.error('Ошибка: не найден канал с ID "{0}"'.format(channel_id), 'channel_not_found')


def _get_json_wrong_channel_id(channel_id):
    return JsonWithStatusResponse.error(
        'Ошибка: идентификатор канала должен быть целым числом, предоставлено: "{0}"'.format(channel_id),
        'id_not_int'
    )

# ------------------------- Lineup -------------------------


@http.require_GET
def lineup_list(request, page=1):
    lineups = models.Lineup.objects.all().order_by('-id')
    return shortcuts.render(request, 'schedule/lineup_list.html', {
        'lineups': pagination.get_page(lineups, page, settings.EFSW_SCHED_LINEUP_LIST_PER_PAGE),
    })


@http.require_GET
def lineup_show(request, lineup_id):
    lineup = shortcuts.get_object_or_404(models.Lineup, pk=lineup_id)
    lineup_table_data = _get_lineup_table_data(lineup)
    return shortcuts.render(request, 'schedule/lineup_show.html', {
        'lineup': lineup,
        'lineup_table_data': lineup_table_data,
    })


@http.require_GET
def lineup_show_current(request, channel_id=None):
    channels_list = list(models.Channel.objects.filter(active=True).order_by('id'))
    if channel_id is None:
        try:
            channel = channels_list[0]
        except IndexError:
            return shortcuts.redirect(urlresolvers.reverse('efsw.schedule:lineup:list'))
    else:
        try:
            channel = [x for x in channels_list if x.id == int(channel_id)][0]
        except IndexError:
            raise Http404('Канал с ID "{0}" не существует'.format(channel_id))
    lineup = _get_current_lineup(channel)
    lineup_table_data = _get_lineup_table_data(lineup) if lineup is not None else None
    return shortcuts.render(request, 'schedule/lineup_show_current.html', {
        'lineup': lineup,
        'lineup_table_data': lineup_table_data,
        'channels_list': channels_list,
        'channel': channel
    })


@http.require_GET
@permission_required('schedule.change_lineup')
def lineup_edit(request, lineup_id):
    return lineup_edit_structure(request, lineup_id)


@http.require_GET
@permission_required('schedule.change_lineup')
def lineup_edit_properties(request, lineup_id):
    lineup = shortcuts.get_object_or_404(models.Lineup, pk=lineup_id)
    return shortcuts.render(request, 'schedule/lineup_edit_properties.html', {
        'lineup': lineup,
        'form': forms.LineupUpdateForm(instance=lineup)
    })


@http.require_GET
@permission_required('schedule.change_lineup')
def lineup_edit_structure(request, lineup_id):
    lineup = shortcuts.get_object_or_404(models.Lineup, pk=lineup_id)
    return shortcuts.render(request, 'schedule/lineup_edit_structure.html', {
        'lineup': lineup,
        'lineup_table_data': _get_lineup_table_data(lineup)
    })


@require_ajax
@http.require_POST
@permission_required('schedule.change_lineup')
def lineup_update_json(request):
    p_result = params.parse_params_or_get_json_error(request.GET, id='\d+')
    if type(p_result) != dict:
        return p_result
    lineup_id = int(p_result['id'])
    try:
        lineup = models.Lineup.objects.get(pk=lineup_id)
    except models.Lineup.DoesNotExist:
        return JsonWithStatusResponse.error(errors.LINEUP_NOT_FOUND.format(lineup_id), 'LINEUP_NOT_FOUND')
    if not lineup.is_editable():
        return JsonWithStatusResponse.error(errors.LINEUP_EDIT_FORBIDDEN.format(lineup_id), 'LINEUP_EDIT_FORBIDDEN')
    form = forms.LineupUpdateForm(request.POST, instance=lineup)
    if form.is_valid():
        updated_lineup = form.save()
        return JsonWithStatusResponse.ok(urlresolvers.reverse('efsw.schedule:lineup:edit', args=(updated_lineup.id, )))
    else:
        return JsonWithStatusResponse.error({'errors': form.errors.as_json()}, 'FORM_INVALID')


@http.require_GET
@permission_required('schedule.add_lineup')
def lineup_new(request):
    return shortcuts.render(request, 'schedule/lineup_new.html', {
        'form': forms.LineupCreateForm()
    })


@require_ajax
@http.require_POST
@permission_required('schedule.add_lineup', raise_exception=True)
def lineup_create_json(request):
    form = forms.LineupCreateForm(request.POST)
    if form.is_valid():
        lineup = form.save()
        models.ProgramPosition.objects.bulk_create([
            models.ProgramPosition(
                dow=d,
                start_time=lineup.start_time,
                end_time=lineup.end_time,
                lineup=lineup
            )
            for d in range(1, 8)
        ])
        return JsonWithStatusResponse.ok(urlresolvers.reverse('efsw.schedule:lineup:show', args=(lineup.id, )))
    else:
        return JsonWithStatusResponse.error({'errors': form.errors.as_json()}, 'FORM_INVALID')


@require_ajax
@http.require_POST
@permission_required('schedule.add_lineup', raise_exception=True)
def lineup_copy_json(request):
    p_result = params.parse_params_or_get_json_error(request.GET, id='\d+')
    if type(p_result) != dict:
        return p_result
    lineup_id = int(p_result['id'])
    try:
        lineup = models.Lineup.objects.get(pk=lineup_id)
    except models.Lineup.DoesNotExist:
        return JsonWithStatusResponse.error(errors.LINEUP_NOT_FOUND.format(lineup_id), 'LINEUP_NOT_FOUND')
    orig_pp = lineup.program_positions.all()
    lineup.pk = None
    lineup.draft = True
    lineup.active_since = None
    lineup.active_until = None
    form = forms.LineupCopyForm(request.POST, instance=lineup)
    if form.is_valid():
        lineup = form.save()

        def remove_pk(pp):
            pp.pk = None
            return pp

        models.ProgramPosition.objects.bulk_create(list(map(remove_pk, orig_pp)))
        return JsonWithStatusResponse.ok(urlresolvers.reverse('efsw.schedule:lineup:show', args=(lineup.id, )))
    else:
        return JsonWithStatusResponse.error({'errors': form.errors.as_json()}, 'FORM_INVALID')


@require_ajax
@http.require_GET
@permission_required('schedule.add_lineup', raise_exception=True)
def lineup_copy_part_modal(request):
    return shortcuts.render(request, 'schedule/_lineup_copy_modal.html', {
        'form': forms.LineupCopyForm()
    })


@require_ajax
@http.require_GET
@permission_required('schedule.change_lineup', raise_exception=True)
def lineup_activate_part_modal(request):
    return shortcuts.render(request, 'schedule/_lineup_activate_modal.html', {
        'form': forms.LineupActivateForm()
    })


@require_ajax
@http.require_POST
@permission_required('schedule.change_lineup', raise_exception=True)
def lineup_activate_json(request):
    p_result = params.parse_params_or_get_json_error(request.GET, id='\d+')
    if type(p_result) != dict:
        return p_result
    lineup_id = int(p_result['id'])
    try:
        lineup = models.Lineup.objects.get(pk=lineup_id)
    except models.Lineup.DoesNotExist:
        return JsonWithStatusResponse.error(errors.LINEUP_NOT_FOUND.format(lineup_id), 'LINEUP_NOT_FOUND')
    if not lineup.draft:
        return JsonWithStatusResponse.error(errors.LINEUP_CANT_ACTIVATE_NON_DRAFT.format(lineup_id),
                                            'LINEUP_CANT_ACTIVATE_NON_DRAFT')
    lineup.draft = False
    form = forms.LineupActivateForm(request.POST, instance=lineup)
    if form.is_valid():
        activation_date = form.cleaned_data['active_since']
        current_active_lineup = _get_current_lineup(lineup.channel, activation_date)
        form.save()
        current_active_lineup.active_until = activation_date - datetime.timedelta(days=1)
        current_active_lineup.save()
        return JsonWithStatusResponse.ok()
    else:
        return JsonWithStatusResponse.error({'errors': form.errors.as_json()}, 'FORM_INVALID')


@require_ajax
@http.require_GET
@permission_required('schedule.change_lineup', raise_exception=True)
def lineup_make_draft_part_modal(request):
    return shortcuts.render(request, 'schedule/_lineup_make_draft_modal.html')


@require_ajax
@http.require_POST
@permission_required('schedule.change_lineup', raise_exception=True)
def lineup_make_draft_json(request):
    p_result = params.parse_params_or_get_json_error(request.GET, id='\d+')
    if type(p_result) != dict:
        return p_result
    lineup_id = int(p_result['id'])
    try:
        lineup = models.Lineup.objects.get(pk=lineup_id)
    except models.Lineup.DoesNotExist:
        return JsonWithStatusResponse.error(errors.LINEUP_NOT_FOUND.format(lineup_id), 'LINEUP_NOT_FOUND')
    if lineup.draft:
        return JsonWithStatusResponse.error(errors.LINEUP_ALREADY_DRAFT.format(lineup_id), 'LINEUP_ALREADY_DRAFT')
    try:
        previous_lineup = models.Lineup.objects.get(
            channel=lineup.channel,
            draft=False,
            active_until=lineup.active_since - datetime.timedelta(days=1)
        )
    except models.Lineup.DoesNotExist:
        previous_lineup = None
    if previous_lineup is not None:
        previous_lineup.active_until = lineup.active_until
        previous_lineup.save()
    lineup.draft = True
    lineup.active_since = None
    lineup.active_until = None
    lineup.save()
    return JsonWithStatusResponse.ok()


@http.require_GET
def lineup_show_part_pp_table_body(request, lineup_id):
    lineup = shortcuts.get_object_or_404(models.Lineup, pk=lineup_id)
    return shortcuts.render(request, 'schedule/_pp_list_table_body.html', {
        'lineup_table_data': _get_lineup_table_data(lineup)
    })


@http.require_GET
def program_list(request, page=1):
    programs = models.Program.objects.all().order_by('name')
    return shortcuts.render(
        request,
        'schedule/program_list.html',
        {
            'programs': pagination.get_page(programs, page, settings.EFSW_SCHED_PROGRAM_LIST_PER_PAGE)
        }
    )


@http.require_GET
@permission_required('schedule.add_program')
def program_new(request):
    form = forms.ProgramCreateForm()
    return shortcuts.render(request, 'schedule/program_new.html', {'form': form})


@require_ajax
@http.require_POST
@permission_required('schedule.add_program', raise_exception=True)
def program_create_json(request):
    form = forms.ProgramCreateForm(request.POST)
    if form.is_valid():
        program = form.save()
        return JsonWithStatusResponse.ok(program.get_absolute_url())
    else:
        return JsonWithStatusResponse.error({'errors': form.errors.as_json()}, 'FORM_INVALID')


@http.require_GET
def program_show(request, program_id):
    program = shortcuts.get_object_or_404(
        models.Program,
        pk=program_id
    )
    return shortcuts.render(request, 'schedule/program_show.html', {'program': program})


@require_ajax
@http.require_GET
def program_show_json(request):

    def format_program_dict(p):
        return {
            'name': p.name,
            'ls_hours': p.lineup_size.hour,
            'ls_minutes': p.lineup_size.minute,
            'age_limit': p.format_age_limit()
        }

    p_result = params.parse_params_or_get_json_error(request.GET, id='\d+')
    if type(p_result) != dict:
        return p_result
    program_id = int(p_result['id'])
    try:
        program = models.Program.objects.get(pk=program_id)
    except models.Program.DoesNotExist:
        return JsonWithStatusResponse.error(errors.PROGRAM_NOT_FOUND.format(program_id), 'PROGRAM_NOT_FOUND')
    return JsonWithStatusResponse(format_program_dict(program))


@require_ajax
@http.require_GET
def pp_show_part_modal(request):
    return shortcuts.render(request, 'schedule/_pp_show_modal.html')


@require_ajax
@http.require_GET
def pp_show_json(request):

    def format_pp_dict(pp):
        return_dict = {
            'id': pp.id,
            'dow': pp.DOW_DICT[pp.dow],
            'start': pp.start_time.strftime('%H:%M'),
            'end': pp.end_time.strftime('%H:%M'),
            'comment': pp.comment,
            'locked': pp.locked
        }
        if pp.program:
            return_dict['program_id'] = pp.program.id
            return_dict['program_name'] = pp.program.name
            return_dict['program_url'] = pp.program.get_absolute_url()
            return_dict['program_ls'] = pp.program.lineup_size.strftime('%H:%M')
            return_dict['program_age_limit'] = pp.program.format_age_limit()
        return return_dict

    p_result = params.parse_params_or_get_json_error(request.GET, id='\d+')
    if type(p_result) != dict:
        return p_result
    pp_id = int(p_result['id'])
    try:
        program_position = models.ProgramPosition.objects.select_related('program').get(pk=pp_id)
    except models.ProgramPosition.DoesNotExist:
        return JsonWithStatusResponse.error(errors.PROGRAM_POSITION_NOT_FOUND.format(pp_id),
                                            'PROGRAM_POSITION_NOT_FOUND')
    return JsonWithStatusResponse(format_pp_dict(program_position))


@require_ajax
@http.require_GET
@permission_required('schedule.change_programposition', raise_exception=True)
def pp_edit_part_modal(request):
    return shortcuts.render(request, 'schedule/_pp_edit_modal.html', {
        'pp_edit_form': forms.ProgramPositionEditForm()
    })


@require_ajax
@http.require_GET
@permission_required('schedule.change_programposition', raise_exception=True)
def pp_edit_json(request):

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
            'similar_pps_dow': [x.dow for x in lineops.get_similar_pp(pp)]
        }
        if pp.program_id:
            return_dict['program_id'] = pp.program_id
        else:
            return_dict['program_id'] = 0
        return return_dict

    p_result = params.parse_params_or_get_json_error(request.GET, id='\d+')
    if type(p_result) != dict:
        return p_result
    pp_id = int(p_result['id'])
    try:
        program_position = models.ProgramPosition.objects.select_related('program').get(pk=pp_id)
    except models.ProgramPosition.DoesNotExist:
        return JsonWithStatusResponse.error(errors.PROGRAM_POSITION_NOT_FOUND.format(pp_id),
                                            'PROGRAM_POSITION_NOT_FOUND')
    return JsonWithStatusResponse(format_pp_dict(program_position))


@require_ajax
@http.require_POST
@permission_required('schedule.change_programposition', raise_exception=True)
def pp_delete_json(request):
    p_result = params.parse_params_or_get_json_error(request.GET, id='\d+')
    if type(p_result) != dict:
        return p_result
    pp_id = int(p_result['id'])
    try:
        program_position = models.ProgramPosition.objects.select_related('program').get(pk=pp_id)
    except models.ProgramPosition.DoesNotExist:
        return JsonWithStatusResponse.error(errors.PROGRAM_POSITION_NOT_FOUND.format(pp_id),
                                            'PROGRAM_POSITION_NOT_FOUND')
    lineup = program_position.lineup
    if not lineup.is_editable():
        return JsonWithStatusResponse.error(errors.LINEUP_EDIT_FORBIDDEN.format(lineup.id), 'LINEUP_EDIT_FORBIDDEN')
    if not program_position.program:
        return JsonWithStatusResponse.error(errors.PROGRAM_POSITION_CANT_DELETE_EMPTY.format(pp_id),
                                            'PROGRAM_POSITION_CANT_DELETE_EMPTY')
    if request.POST.get('r', None) is not None:
        form = forms.ProgramPositionRepeatForm(request.POST)
        if form.is_valid():
            for pp in [x for x in lineops.get_similar_pp(program_position) if str(x.dow) in form.cleaned_data.get('r')]:
                _pp_delete(pp)
        else:
            return JsonWithStatusResponse.error('Неправильный формат списка повторов', 'FORM_INVALID')
    _pp_delete(program_position)
    return JsonWithStatusResponse.ok()


@require_ajax
@http.require_POST
@permission_required('schedule.change_programposition', raise_exception=True)
def pp_update_json(request):
    p_result = params.parse_params_or_get_json_error(request.GET, id='\d+')
    if type(p_result) != dict:
        return p_result
    pp_id = int(p_result['id'])
    try:
        program_position = models.ProgramPosition.objects.select_related('program').get(pk=pp_id)
    except models.ProgramPosition.DoesNotExist:
        return JsonWithStatusResponse.error(errors.PROGRAM_POSITION_NOT_FOUND.format(pp_id),
                                            'PROGRAM_POSITION_NOT_FOUND')
    lineup = program_position.lineup
    if not lineup.is_editable():
        return JsonWithStatusResponse.error(errors.LINEUP_EDIT_FORBIDDEN.format(lineup.id), 'LINEUP_EDIT_FORBIDDEN')
    form = forms.ProgramPositionEditForm(request.POST)
    if not form.is_valid():
        return JsonWithStatusResponse.error({'errors': form.errors.as_json()}, 'FORM_INVALID')
    repeat_for = [
        x
        for x in lineops.get_similar_pp(program_position)
        if str(x.dow) in form.cleaned_data.get('r')
    ]
    program_position.program = form.cleaned_data.get('p', None)
    program_position.locked = form.cleaned_data['l']
    program_position.comment = form.cleaned_data['c']
    old_start_time = program_position.start_time
    old_end_time = program_position.end_time
    program_position.start_time = datetime.time(form.cleaned_data['st_h'], form.cleaned_data['st_m'])
    program_position.end_time = datetime.time(form.cleaned_data['et_h'], form.cleaned_data['et_m'])
    try:
        program_position.full_clean()
    except ValidationError as e:
        return JsonWithStatusResponse.error({'errors': json.dumps(e.message_dict)}, 'MODEL_INVALID')
    if old_start_time == program_position.start_time and old_end_time == program_position.end_time:
        # Если фрагмент не меняет свою длительность
        if not lineops.pp_is_empty(program_position):
            # и при этом становится или остаётся не пустым
            program_position.save()
            for pp in repeat_for:
                pp.program = program_position.program
                pp.comment = program_position.comment
                pp.locked = program_position.locked
                pp.save()
        else:
            # если же становится или остаётся пустым
            _pp_delete(program_position)
            for pp in repeat_for:
                _pp_delete(pp)
    else:
        # А если всё-таки меняет длительность
        if lineops.pp_is_empty(program_position):
            return JsonWithStatusResponse.error(
                {
                    'errors': json.dumps(
                        {'__all__': [errors.PROGRAM_POSITION_CANT_RESIZE_EMPTY.format(program_position.id)]}
                    )
                },
                'PROGRAM_POSITION_CANT_RESIZE_EMPTY'
            )
        start_time = program_position.start_time
        end_time = program_position.end_time
        if (old_end_time > old_start_time and not (old_start_time <= start_time < end_time <= old_end_time)) \
                or (old_end_time < old_start_time and not (
                    (start_time >= old_start_time or start_time < old_end_time)
                    and (end_time <= old_end_time or end_time > old_start_time)
                )):
            return JsonWithStatusResponse.error(
                {
                    'errors': json.dumps(
                        {'__all__': [errors.PROGRAM_POSITION_NEW_OUT_OF_OLD_BOUNDS]}
                    )
                },
                'PROGRAM_POSITION_NEW_OUT_OF_OLD_BOUNDS'
            )
        program_position.save()
        for pp in repeat_for:
            pp.program = program_position.program
            pp.comment = program_position.comment
            pp.locked = program_position.locked
            pp.start_time = program_position.start_time
            pp.end_time = program_position.end_time
            pp.save()
        if old_start_time != start_time:
            # нужно добавить пустое место перед фрагментом - а вдруг уже есть?
            for pp in [program_position] + repeat_for:
                previous_pp = lineops.get_previous_pp_by_time(pp.lineup, pp.dow, old_start_time)
                if previous_pp is not None and lineops.pp_is_empty(previous_pp):
                    previous_pp.end_time = start_time
                    previous_pp.save()
                else:
                    prepend_pp = models.ProgramPosition(
                        start_time=old_start_time,
                        end_time=start_time,
                        dow=pp.dow,
                        lineup=pp.lineup,
                    )
                    prepend_pp.save()
        if old_end_time != end_time:
            # нужно добавить пустое место после фрагмента - а вдруг уже есть?
            for pp in [program_position] + repeat_for:
                next_pp = lineops.get_next_pp_by_time(pp.lineup, pp.dow, old_end_time)
                if next_pp is not None and lineops.pp_is_empty(next_pp):
                    next_pp.start_time = end_time
                    next_pp.save()
                else:
                    append_pp = models.ProgramPosition(
                        start_time=end_time,
                        end_time=old_end_time,
                        dow=pp.dow,
                        lineup=pp.lineup,
                    )
                    append_pp.save()
    return JsonWithStatusResponse.ok()


@http.require_GET
def channel_list(request, page=1):
    return shortcuts.render(request, 'schedule/channel_list.html', {
        'channels': pagination.get_page(models.Channel.objects.all(), page, settings.EFSW_SCHED_CHANNEL_LIST_PER_PAGE)
    })


@http.require_GET
@permission_required('schedule.add_channel')
def channel_new(request):
    return shortcuts.render(request, 'schedule/channel_new.html', {
        'form': forms.ChannelCreateForm()
    })


@http.require_GET
def channel_show_lineups(request, channel_id, page=1):
    channel = shortcuts.get_object_or_404(models.Channel, pk=channel_id)
    return shortcuts.render(request, 'schedule/channel_show_lineups.html', {
        'lineups': pagination.get_page(channel.lineups.all(), page, settings.EFSW_SCHED_LINEUP_LIST_PER_PAGE),
        'channel': channel
    })


@http.require_GET
@permission_required('schedule.change_channel')
def channel_edit(request, channel_id):
    channel = shortcuts.get_object_or_404(models.Channel, pk=channel_id)
    form = forms.ChannelCreateForm(instance=channel)
    return shortcuts.render(request, 'schedule/channel_edit.html', {
        'channel': channel,
        'form': form
    })


@require_ajax
@http.require_POST
@permission_required('schedule.add_channel', raise_exception=True)
def channel_create_json(request):
    form = forms.ChannelCreateForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonWithStatusResponse.ok(urlresolvers.reverse('efsw.schedule:channel:list'))
    else:
        return JsonWithStatusResponse.error({'errors': form.errors.as_json()}, 'FORM_INVALID')


@require_ajax
@http.require_POST
@permission_required('schedule.change_channel', raise_exception=True)
def channel_update_json(request):
    p_result = params.parse_params_or_get_json_error(request.GET, id='\d+')
    if type(p_result) != dict:
        return p_result
    channel_id = int(p_result['id'])
    try:
        channel = models.Channel.objects.get(pk=channel_id)
    except models.Channel.DoesNotExist:
        return JsonWithStatusResponse.error(errors.CHANNEL_NOT_FOUND.format(channel_id), 'CHANNEL_NOT_FOUND')
    form = forms.ChannelCreateForm(request.POST, instance=channel)
    if form.is_valid():
        form.save()
        return JsonWithStatusResponse.ok(urlresolvers.reverse('efsw.schedule:channel:list'))
    else:
        return JsonWithStatusResponse.error({'errors': form.errors.as_json()}, 'FORM_INVALID')


@require_ajax
@http.require_POST
@permission_required('schedule.change_channel', raise_exception=True)
def channel_activate_json(request):
    p_result = params.parse_params_or_get_json_error(request.GET, id='\d+')
    if type(p_result) != dict:
        return p_result
    channel_id = int(p_result['id'])
    try:
        channel = models.Channel.objects.get(pk=channel_id)
    except models.Channel.DoesNotExist:
        return JsonWithStatusResponse.error(errors.CHANNEL_NOT_FOUND.format(channel_id), 'CHANNEL_NOT_FOUND')
    if channel.active:
        return JsonWithStatusResponse.error(errors.CHANNEL_ALREADY_ACTIVE.format(channel_id), 'CHANNEL_ALREADY_ACTIVE')
    channel.active = True
    channel.save()
    return JsonWithStatusResponse.ok()


@require_ajax
@http.require_POST
@permission_required('schedule.change_channel', raise_exception=True)
def channel_deactivate_json(request):
    p_result = params.parse_params_or_get_json_error(request.GET, id='\d+')
    if type(p_result) != dict:
        return p_result
    channel_id = int(p_result['id'])
    try:
        channel = models.Channel.objects.get(pk=channel_id)
    except models.Channel.DoesNotExist:
        return JsonWithStatusResponse.error(errors.CHANNEL_NOT_FOUND.format(channel_id), 'CHANNEL_NOT_FOUND')
    if not channel.active:
        return JsonWithStatusResponse.error(errors.CHANNEL_ALREADY_NOT_ACTIVE.format(channel_id),
                                            'CHANNEL_ALREADY_NOT_ACTIVE')
    channel.active = False
    channel.save()
    return JsonWithStatusResponse.ok()
