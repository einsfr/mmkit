import os
import math

from django.test import TestCase
from django.core import urlresolvers, paginator

from mmkit.conf import settings
from efsw.conversion import models
from efsw.common.utils.testcases import LoginRequiredTestCase, JsonResponseTestCase
from efsw.conversion.fixtures import conversionprofile, conversiontask
from efsw.storage.models import FileStorage


class TaskListTestCase(TestCase):

    def test_list(self):
        response = self.client.get(urlresolvers.reverse('efsw.conversion:task:list'))
        short_count = getattr(settings, 'EFSW_CONVERTER_TASKS_SHORT_LIST_COUNT')

        finished_count = models.ConversionTask.objects.filter(
            status__in=[models.ConversionTask.STATUS_ERROR, models.ConversionTask.STATUS_COMPLETED,
                        models.ConversionTask.STATUS_CANCELED]
        ).count()
        finished_count = finished_count if finished_count < short_count else short_count
        self.assertEqual(len(response.context['tasks_finished']), finished_count)
        self.assertTrue(response.context['tasks_finished_more'] or finished_count <= short_count)

        unknown_count = models.ConversionTask.objects.filter(
            status=models.ConversionTask.STATUS_UNKNOWN
        ).count()
        unknown_count = unknown_count if unknown_count < short_count else short_count
        self.assertEqual(len(response.context['tasks_unknown']), unknown_count)
        self.assertTrue(response.context['tasks_unknown_more'] or unknown_count <= short_count)

        in_progress_count = models.ConversionTask.objects.filter(
            status__in=[models.ConversionTask.STATUS_START_WAITING, models.ConversionTask.STATUS_IN_PROGRESS,
                        models.ConversionTask.STATUS_STARTED]
        ).count()
        in_progress_count = in_progress_count if in_progress_count < short_count else short_count
        self.assertEqual(len(response.context['tasks_in_progress']), in_progress_count)
        self.assertTrue(response.context['tasks_in_progress_more'] or in_progress_count <= short_count)

        enqueued_count = models.ConversionTask.objects.filter(status=models.ConversionTask.STATUS_ENQUEUED).count()
        enqueued_count = enqueued_count if enqueued_count < short_count else short_count
        self.assertEqual(len(response.context['tasks_enqueued']), enqueued_count)
        self.assertTrue(response.context['tasks_enqueued_more'] or enqueued_count <= short_count)

    def test_list_finished(self):
        response = self.client.get(urlresolvers.reverse('efsw.conversion:task:list_finished'))
        self.assertEqual(
            len(response.context['tasks_finished']),
            models.ConversionTask.objects.filter(
                status__in=[models.ConversionTask.STATUS_ERROR, models.ConversionTask.STATUS_COMPLETED,
                            models.ConversionTask.STATUS_CANCELED]
            ).count()
        )

    def test_list_unknown(self):
        response = self.client.get(urlresolvers.reverse('efsw.conversion:task:list_unknown'))
        self.assertEqual(
            len(response.context['tasks_unknown']),
            models.ConversionTask.objects.filter(
                status=models.ConversionTask.STATUS_UNKNOWN
            ).count()
        )

    def test_list_in_progress(self):
        response = self.client.get(urlresolvers.reverse('efsw.conversion:task:list_in_progress'))
        self.assertEqual(
            len(response.context['tasks_in_progress']),
            models.ConversionTask.objects.filter(
                status__in=[models.ConversionTask.STATUS_START_WAITING, models.ConversionTask.STATUS_IN_PROGRESS,
                            models.ConversionTask.STATUS_STARTED]
            ).count()
        )

    def test_list_enqueued(self):
        response = self.client.get(urlresolvers.reverse('efsw.conversion:task:list_enqueued'))
        self.assertEqual(
            len(response.context['tasks_enqueued']),
            models.ConversionTask.objects.filter(status=models.ConversionTask.STATUS_ENQUEUED).count()
        )


class TaskNewTestCase(LoginRequiredTestCase):

    def test_variables(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.conversion:task:new'))
        self.assertIn('form', response.context)
        self.assertIn('input_formset', response.context)
        self.assertIn('output_formset', response.context)


class TaskCreateJsonTestCase(LoginRequiredTestCase, JsonResponseTestCase):

    fixtures = ['filestorage.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.conversion:task:create_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(405, response.status_code)

    def test_invalid_form(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'FORM_INVALID')

    def test_invalid_formset(self):
        conversionprofile.load_data()
        self._login_user()
        data = {
            'name': 'Тестовое имя',
            'profile': 1
        }
        response = self.client.post(self.url, data)
        self.assertJsonError(response, 'FORMSET_ERROR')
        data = {
            'name': 'Тестовое имя',
            'profile': 1,
            'inputs-TOTAL_FORMS': 1,
            'inputs-INITIAL_FORMS': 1,
            'inputs-MIN_NUM_FORMS': 1,
            'inputs-MAX_NUM_FORMS': 1,
            'outputs-TOTAL_FORMS': 1,
            'outputs-INITIAL_FORMS': 1,
            'outputs-MIN_NUM_FORMS': 1,
            'outputs-MAX_NUM_FORMS': 1,
        }
        response = self.client.post(self.url, data)
        self.assertJsonError(response, 'FORMSET_INVALID')
        errors = self.get_json_errors(response)
        self.assertIn('inputs', errors)
        self.assertIn('outputs', errors)

    def test_valid(self):
        conversionprofile.load_data()
        self._login_user()
        FileStorage.initiate_storage_root(FileStorage.INIT_MODE_SKIP_IF_EXISTS)
        fs_in = FileStorage.objects.get(pk='1ac9873a-8cf0-49e1-8a9a-7709930aa8af')
        fs_in.initiate_storage_base(FileStorage.INIT_MODE_SKIP_IF_EXISTS)
        fs_path = fs_in.get_base_path()
        open(os.path.join(fs_path, 'in'), 'w').close()
        fs_out = FileStorage.objects.get(pk='11e00904-0f3d-4bfa-a3a9-9c716f87bc01')
        fs_out.initiate_storage_base(FileStorage.INIT_MODE_SKIP_IF_EXISTS)
        fs_path = fs_out.get_base_path()
        try:
            os.remove(os.path.join(fs_path, 'out'))
        except FileNotFoundError:
            pass
        data = {
            'name': 'Тестовое имя',
            'profile': 1,
            'inputs-TOTAL_FORMS': 1,
            'inputs-INITIAL_FORMS': 1,
            'inputs-MIN_NUM_FORMS': 1,
            'inputs-MAX_NUM_FORMS': 1,
            'outputs-TOTAL_FORMS': 1,
            'outputs-INITIAL_FORMS': 1,
            'outputs-MIN_NUM_FORMS': 1,
            'outputs-MAX_NUM_FORMS': 1,
            'inputs-0-storage': '1ac9873a-8cf0-49e1-8a9a-7709930aa8af',
            'inputs-0-path': 'in',
            'outputs-0-storage': '11e00904-0f3d-4bfa-a3a9-9c716f87bc01',
            'outputs-0-path': 'out',
        }
        response = self.client.post(self.url, data)
        self.assertJsonOk(response)


class TaskShowTestCase(TestCase):

    def setUp(self):
        conversiontask.load_data()

    def test_404(self):
        response = self.client.get(urlresolvers.reverse(
            'efsw.conversion:task:show', args=('e0593092-fbc5-4b20-10f4-677f8954220f', ))
        )
        self.assertEqual(404, response.status_code)

    def test_normal(self):
        response = self.client.get(urlresolvers.reverse(
            'efsw.conversion:task:show', args=('e0593092-fbc5-4b20-99f4-677f8954220f', ))
        )
        self.assertEqual(200, response.status_code)
        self.assertIn('task', response.context)


class ProfileListTestCase(TestCase):

    def setUp(self):
        conversionprofile.load_data()

    def test_list(self):
        response = self.client.get(urlresolvers.reverse('efsw.conversion:profile:list'))
        self.assertIsInstance(response.context['profiles'], paginator.Page)
        page_count = math.ceil(
            models.ConversionProfile.objects.count() / getattr(settings, 'EFSW_CONVERTER_PROFILES_PER_PAGE')
        )
        self.assertEqual(1, response.context['profiles'].number)
        self.assertEqual(page_count, response.context['profiles'].paginator.num_pages)


class ProfileShowTestCase(TestCase):

    def setUp(self):
        conversionprofile.load_data()

    def test_404(self):
        response = self.client.get(urlresolvers.reverse('efsw.conversion:profile:show', args=(1000000, )))
        self.assertEqual(404, response.status_code)

    def test_normal(self):
        response = self.client.get(urlresolvers.reverse('efsw.conversion:profile:show', args=(1, )))
        self.assertEqual(200, response.status_code)
        self.assertIn('profile', response.context)


class ProfileNewTestCase(LoginRequiredTestCase):

    def test_variables(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.conversion:profile:new'))
        self.assertIn('form', response.context)
        self.assertIn('input_formset', response.context)
        self.assertIn('output_formset', response.context)


class ProfileCreateJsonTestCase(LoginRequiredTestCase, JsonResponseTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.conversion:profile:create_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(405, response.status_code)

    def test_invalid_form(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'FORM_INVALID')

    def test_invalid_formset(self):
        self._login_user()
        data = {
            'name': 'Тестовый профиль'
        }
        response = self.client.post(self.url, data)
        self.assertJsonError(response, 'FORMSET_ERROR')
        data = {
            'name': 'Тестовое имя',
            'inputs-TOTAL_FORMS': 1,
            'inputs-INITIAL_FORMS': 1,
            'inputs-MIN_NUM_FORMS': 1,
            'inputs-MAX_NUM_FORMS': 1,
            'outputs-TOTAL_FORMS': 1,
            'outputs-INITIAL_FORMS': 1,
            'outputs-MIN_NUM_FORMS': 1,
            'outputs-MAX_NUM_FORMS': 1,
        }
        response = self.client.post(self.url, data)
        self.assertJsonOk(response)
        profile = models.ConversionProfile.objects.get(name='Тестовое имя')
        self.assertEqual(1, len(profile.args_builder.inputs))
        self.assertEqual(1, len(profile.args_builder.outputs))


class ProfileShowJson(JsonResponseTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.conversion:profile:show_json')

    def setUp(self):
        conversionprofile.load_data()

    def test_invalid(self):
        response = self.client.get(self.url)
        self.assertJsonError(response, 'REQUIRED_REQUEST_PARAMETER_IS_MISSING')
        response = self.client.get('{0}?id=abc'.format(self.url))
        self.assertJsonError(response, 'UNEXPECTED_REQUEST_PARAMETER_VALUE')
        response = self.client.get('{0}?id=1000000'.format(self.url))
        self.assertJsonError(response, 'PROFILE_NOT_FOUND')

    def test_valid(self):
        response = self.client.get('{0}?id=1'.format(self.url))
        self.assertJsonOk(response)
        data = self.get_json_data(response)
        self.assertIn('name', data)
        self.assertIn('description', data)
        self.assertIn('inputs', data)
        self.assertIn('outputs', data)
        self.assertEqual(1, len(data['inputs']))
        self.assertEqual(1, len(data['outputs']))

