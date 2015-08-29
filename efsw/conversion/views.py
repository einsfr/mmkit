import json
import uuid
import datetime

from django import shortcuts
from django.conf import settings
from django.views.decorators import http
from django.forms.formsets import formset_factory
from django.core import urlresolvers
from django.core.exceptions import ValidationError

from efsw.conversion import models, forms, errors
from efsw.conversion.converter import args
from efsw.conversion.storage.iopathprovider import FileStorageIOPathProvider
from efsw.common.db import pagination
from efsw.common.http.response import JsonWithStatusResponse
from efsw.common.http.decorators import require_ajax
from efsw.common.utils import params


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


@require_ajax
@http.require_POST
def task_create_json(request):
    task_form = forms.TaskCreateForm(request.POST)
    if task_form.is_valid():
        inputs_count = len(task_form.cleaned_data['profile'].args_builder.inputs)
        outputs_count = len(task_form.cleaned_data['profile'].args_builder.outputs)
        input_formset = formset_factory(forms.InputLocationForm, formset=forms.BaseInputLocationFormSet,
                                        max_num=inputs_count, min_num=inputs_count, validate_max=True,
                                        validate_min=True)(request.POST, prefix='inputs')
        output_formset = formset_factory(forms.OutputLocationForm, formset=forms.BaseOutputLocationFormSet,
                                         max_num=outputs_count, min_num=outputs_count, validate_max=True,
                                         validate_min=True)(request.POST, prefix='outputs')
        if input_formset.is_valid() and output_formset.is_valid():
            ct = models.ConversionTask()
            name = task_form.cleaned_data['name']
            ct.name = name if name else '{0}: создано {1}'.format(
                uuid.uuid4(), datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            )

            def _parse_io_form(f):
                return FileStorageIOPathProvider(f.cleaned_data['storage'].id, f.cleaned_data['path'])

            ct.io_conf = args.IOPathConfiguration(
                list(map(_parse_io_form, input_formset.forms)),
                list(map(_parse_io_form, output_formset.forms))
            )
            ct.conv_profile = task_form.cleaned_data['profile']
            ct.save()
            return JsonWithStatusResponse.ok(urlresolvers.reverse('efsw.conversion:task:show', args=(ct.id, )))
        else:
            form_errors = {}
            if input_formset.errors:
                form_errors['inputs'] = input_formset.errors
            if output_formset.errors:
                form_errors['outputs'] = output_formset.errors
            inputs_nf_errors = input_formset.non_form_errors()
            if inputs_nf_errors:
                form_errors['inputs__all__'] = inputs_nf_errors
            outputs_nf_errors = output_formset.non_form_errors()
            if outputs_nf_errors:
                form_errors['outputs__all__'] = outputs_nf_errors
            return JsonWithStatusResponse.error({'errors': json.dumps(form_errors)}, 'FORM_INVALID')
    else:
        return JsonWithStatusResponse.error({'errors': task_form.errors.as_json()}, 'FORM_INVALID')


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


@require_ajax
@http.require_GET
def profile_show_json(request):
    p_result = params.parse_params_or_get_json_error(request.GET, id=r'\d+')
    if type(p_result) != dict:
        return p_result
    profile_id = p_result['id']
    try:
        profile = models.ConversionProfile.objects.get(pk=profile_id)
    except models.ConversionProfile.DoesNotExist:
        return JsonWithStatusResponse.error(errors.PROFILE_NOT_FOUND.format(profile_id), 'PROFILE_NOT_FOUND')
    return JsonWithStatusResponse.ok({
        'name': profile.name,
        'description': profile.description,
        'inputs': [
            {
                'position': p,
                'comment': i.comment,
                'allowed_ext': i.allowed_ext
            }
            for p, i in enumerate(profile.args_builder.inputs)
        ],
        'outputs': [
            {
                'position': p,
                'comment': o.comment,
                'allowed_ext': o.allowed_ext
            }
            for p, o in enumerate(profile.args_builder.outputs)
        ]
    })
