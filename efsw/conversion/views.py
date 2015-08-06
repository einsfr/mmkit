from django import shortcuts
from django.conf import settings
from django.views.decorators import http
from django.forms.formsets import formset_factory

from efsw.conversion import models, forms
from efsw.common.db import pagination
from efsw.common.http.response import JsonWithStatusResponse


def _get_json_profile_not_found(profile_id):
    return JsonWithStatusResponse.error(
        'Ошибка: профиль с ID "{0}" не существует.'.format(profile_id),
        'profile_not_found'
    )


def _get_json_profile_wrong_id(profile_id):
    return JsonWithStatusResponse.error(
        'Ошибка: идентификатор профиля должен быть целым числом, предоставлено: "{0}".'.format(profile_id),
        'id_not_int'
    )


@http.require_GET
def task_list(request):
    tasks_count = settings.EFSW_CONVERTER_TASKS_SHORT_LIST_COUNT
    tasks_finished = models.ConversionTask.objects.filter(
        status__in=[models.ConversionTask.STATUS_ERROR, models.ConversionTask.STATUS_COMPLETED,
                    models.ConversionTask.STATUS_CANCELED]
    ).order_by('order')[:tasks_count + 1]
    tasks_finished_more = len(tasks_finished) > tasks_count
    tasks_unknown = models.ConversionTask.objects.filter(
        status=models.ConversionTask.STATUS_UNKNOWN
    ).order_by('order')[:tasks_count + 1]
    tasks_unknown_more = len(tasks_unknown) > tasks_count
    tasks_in_progress = models.ConversionTask.objects.filter(
        status__in=[models.ConversionTask.STATUS_START_WAITING, models.ConversionTask.STATUS_IN_PROGRESS,
                    models.ConversionTask.STATUS_STARTED]
    ).order_by('order')[:tasks_count + 1]
    tasks_in_progress_more = len(tasks_in_progress) > tasks_count
    tasks_enqueued = models.ConversionTask.objects.filter(
        status=models.ConversionTask.STATUS_ENQUEUED
    ).order_by('order')[:tasks_count + 1]
    tasks_enqueued_more = len(tasks_enqueued) > tasks_count
    return shortcuts.render(request, 'conversion/task_list.html', {
        'tasks_finished': tasks_finished[:tasks_count],
        'tasks_finished_more': tasks_finished_more,
        'tasks_unknown': tasks_unknown[:tasks_count],
        'tasks_unknown_more': tasks_unknown_more,
        'tasks_in_progress': tasks_in_progress[:tasks_count],
        'tasks_in_progress_more': tasks_in_progress_more,
        'tasks_enqueued': tasks_enqueued[:tasks_count],
        'tasks_enqueued_more': tasks_enqueued_more,
    })


@http.require_GET
def task_list_finished(request):
    tasks_finished = models.ConversionTask.objects.filter(
        status__in=[models.ConversionTask.STATUS_ERROR, models.ConversionTask.STATUS_COMPLETED,
                    models.ConversionTask.STATUS_CANCELED]
    ).order_by('order')
    return shortcuts.render(request, 'conversion/task_list_finished.html', {
        'tasks_finished': tasks_finished
    })


@http.require_GET
def task_list_unknown(request):
    tasks_unknown = models.ConversionTask.objects.filter(
        status=models.ConversionTask.STATUS_UNKNOWN
    ).order_by('order')
    return shortcuts.render(request, 'conversion/task_list_unknown.html', {
        'tasks_unknown': tasks_unknown
    })


@http.require_GET
def task_list_in_progress(request):
    tasks_in_progress = models.ConversionTask.objects.filter(
        status__in=[models.ConversionTask.STATUS_START_WAITING, models.ConversionTask.STATUS_IN_PROGRESS,
                    models.ConversionTask.STATUS_STARTED]
    ).order_by('order')
    return shortcuts.render(request, 'conversion/task_list_in_progress.html', {
        'tasks_in_progress': tasks_in_progress
    })


@http.require_GET
def task_list_enqueued(request):
    tasks_enqueued = models.ConversionTask.objects.filter(
        status=models.ConversionTask.STATUS_ENQUEUED
    ).order_by('order')
    return shortcuts.render(request, 'conversion/task_list_enqueued.html', {
        'tasks_enqueued': tasks_enqueued
    })


@http.require_GET
def task_new(request):
    input_formset_class = formset_factory(forms.InputLocationForm, min_num=0, max_num=0, extra=0)
    output_formset_class = formset_factory(forms.OutputLocationForm, min_num=0, max_num=0, extra=0)
    return shortcuts.render(request, 'conversion/task_new.html', {
        'form': forms.TaskCreateForm(),
        'input_formset': input_formset_class(prefix='inputs'),
        'output_formset': output_formset_class(prefix='outputs'),
    })


@http.require_GET
def task_show(request, task_id):
    task = shortcuts.get_object_or_404(
        models.ConversionTask,
        pk=task_id
    )
    return shortcuts.render(request, 'conversion/task_show.html', {
        'task': task
    })


@http.require_GET
def profile_list(request, page=1):
    profiles = models.ConversionProfile.objects.all().order_by('name')
    profiles_page = pagination.get_page(profiles, page, settings.EFSW_CONVERTER_PROFILES_PER_PAGE)
    return shortcuts.render(request, 'conversion/profile_list.html', {
        'profiles': profiles_page
    })


@http.require_GET
def profile_show(request, profile_id):
    profile = shortcuts.get_object_or_404(models.ConversionProfile, pk=profile_id)
    return shortcuts.render(request, 'conversion/profile_show.html', {
        'profile': profile
    })


@http.require_GET
def profile_show_json(request):
    profile_id = request.GET.get('id', None)
    try:
        profile = models.ConversionProfile.objects.get(pk=profile_id)
    except models.ConversionProfile.DoesNotExist:
        return _get_json_profile_not_found(profile_id)
    except ValueError:
        return _get_json_profile_wrong_id(profile_id)
    return JsonWithStatusResponse.ok({
        'name': profile.name,
        'description': profile.description,
    })
