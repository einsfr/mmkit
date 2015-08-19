import json
import datetime

from django.test import TestCase
from django.core import urlresolvers, paginator
from django.core.management import call_command

from efsw.schedule import models
from efsw.common.utils.testcases import LoginRequiredTestCase, JsonResponseTestCase


# ------------------------- Lineup -------------------------


class LineupListTestCase(TestCase):

    fixtures = ['channel.json', 'lineup.json']

    def test_list(self):
        response = self.client.get(urlresolvers.reverse('efsw.schedule:lineup:list'))
        self.assertIsInstance(response.context['lineups'], paginator.Page)
        self.assertEqual(1, response.context['lineups'].number)


class LineupShowTestCase(TestCase):

    fixtures = ['channel.json', 'lineup.json', 'program.json', 'programposition.json']

    def test_404(self):
        response = self.client.get(urlresolvers.reverse('efsw.schedule:lineup:show', args=(1000000, )))
        self.assertEqual(404, response.status_code)

    def test_table_data_structure(self):
        lineup_id = 1
        response = self.client.get(urlresolvers.reverse('efsw.schedule:lineup:show', args=(lineup_id, )))
        table_data = response.context['lineup_table_data']
        for _ in ['rows', 'lineup_start_time', 'lineup_end_time']:
            self.assertIn(_, table_data)
        self.assertIsInstance(table_data['rows'], list)
        self.assertIsInstance(table_data['rows'][0], list)
        self.assertIsInstance(table_data['rows'][0][0], datetime.time)
        self.assertIn('pp', table_data['rows'][0][1])
        self.assertIn('row_span', table_data['rows'][0][1])
        self.assertIsInstance(table_data['rows'][0][1]['pp'], models.ProgramPosition)
        pps = models.Lineup.objects.get(pk=lineup_id).program_positions.all()
        self.assertEqual(
            sorted([col['pp'].id for row in table_data['rows'] for col in row if isinstance(col, dict)]),
            sorted([pp.id for pp in pps])
        )


class LineupShowCurrentTestCase(TestCase):

    fixtures = ['channel.json', 'lineup.json', 'program.json', 'programposition.json']

    def test_no_channels(self):
        for ch in models.Channel.objects.all():
            ch.delete()
        response = self.client.get(urlresolvers.reverse('efsw.schedule:lineup:show_current'))
        self.assertEqual(302, response.status_code)
        response = self.client.get(urlresolvers.reverse('efsw.schedule:lineup:show_current_channel', args=(1, )))
        self.assertEqual(404, response.status_code)
        call_command('loaddata', 'channel.json', verbosity=0)


class LineupEditPropertiesTestCase(LoginRequiredTestCase):

    fixtures = []

    def test_404(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.schedule:lineup:edit_properties', args=(1000000, )))
        self.assertEqual(404, response.status_code)


class LineupEditStructureTestCase(LoginRequiredTestCase):

    fixtures = []

    def test_404(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.schedule:lineup:edit_structure', args=(1000000, )))
        self.assertEqual(404, response.status_code)


class LineupUpdateJsonTestCase(LoginRequiredTestCase, JsonResponseTestCase):

    fixtures = ['channel.json', 'lineup.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.schedule:lineup:update_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(405, response.status_code)

    def test_not_found(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'REQUIRED_REQUEST_PARAMETER_IS_MISSING')

    def test_not_editable(self):
        self._login_user()
        response = self.client.post('{0}{1}'.format(self.url, '?id=1'))
        self.assertJsonError(response, 'LINEUP_EDIT_FORBIDDEN')

    def test_invalid(self):
        self._login_user()
        response = self.client.post(
            '{0}{1}'.format(self.url, '?id=2'),
            {'name': ''}
        )
        self.assertJsonError(response, 'FORM_INVALID')

    def test_valid(self):
        self._login_user()
        response = self.client.post(
            '{0}{1}'.format(self.url, '?id=2'),
            {'name': 'После тестового обновления имя выглядит так'}
        )
        self.assertJsonOk(
            response,
            data=urlresolvers.reverse('efsw.schedule:lineup:edit', args=(2, ))
        )


class LineupCreateJsonTestCase(LoginRequiredTestCase, JsonResponseTestCase):

    fixtures = ['lineup.json', 'channel.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.schedule:lineup:create_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(405, response.status_code)

    def test_invalid(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'FORM_INVALID')

    def test_valid(self):
        self._login_user()
        response = self.client.post(
            self.url,
            {
                'name': 'Название сетки вещания для теста',
                'start_time': '06:00',
                'end_time': '06:00',
                'channel': 1
            }
        )
        lineup_id = models.Lineup.objects.count()
        self.assertJsonOk(
            response,
            data=urlresolvers.reverse('efsw.schedule:lineup:show', args=(lineup_id, ))
        )
        self.assertEqual(7, models.Lineup.objects.get(pk=lineup_id).program_positions.count())


class LineupCopyJsonTestCase(LoginRequiredTestCase, JsonResponseTestCase):

    fixtures = ['channel.json', 'lineup.json', 'programposition.json', 'program.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.schedule:lineup:copy_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(405, response.status_code)

    def test_wrong_id(self):
        self._login_user()
        for i in ['', 'non-int']:
            response = self.client.post('{0}?id={1}'.format(self.url, i))
            self.assertJsonError(response, 'UNEXPECTED_REQUEST_PARAMETER_VALUE')

    def test_404(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'REQUIRED_REQUEST_PARAMETER_IS_MISSING')
        response = self.client.post('{0}?id={1}'.format(self.url, 1000000))
        self.assertJsonError(response, 'LINEUP_NOT_FOUND')

    def test_invalid(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.url, 1))
        self.assertJsonError(response, 'FORM_INVALID')

    def test_valid(self):
        self._login_user()
        response = self.client.post(
            '{0}?id={1}'.format(self.url, 1),
            {
                'name': 'Название для скопированной сетки'
            }
        )
        lineup_id = models.Lineup.objects.count()
        self.assertJsonOk(
            response,
            data=urlresolvers.reverse('efsw.schedule:lineup:show', args=(lineup_id, ))
        )
        self.assertEqual(
            models.Lineup.objects.get(pk=1).program_positions.count(),
            models.Lineup.objects.get(pk=lineup_id).program_positions.count()
        )


class LineupActivateJsonTestCase(LoginRequiredTestCase, JsonResponseTestCase):

    fixtures = ['channel.json', 'lineup.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.schedule:lineup:activate_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(405, response.status_code)

    def test_wrong_id(self):
        self._login_user()
        for i in ['', 'non-int']:
            response = self.client.post('{0}?id={1}'.format(self.url, i))
            self.assertJsonError(response, 'UNEXPECTED_REQUEST_PARAMETER_VALUE')

    def test_404(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'REQUIRED_REQUEST_PARAMETER_IS_MISSING')
        response = self.client.post('{0}?id={1}'.format(self.url, 1000000))
        self.assertJsonError(response, 'LINEUP_NOT_FOUND')

    def test_non_draft(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.url, 1))
        self.assertJsonError(response, 'LINEUP_CANT_ACTIVATE_NON_DRAFT')

    def test_invalid(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.url, 2))
        self.assertJsonError(response, 'FORM_INVALID')


class LineupMakeDraftJsonTestCase(LoginRequiredTestCase, JsonResponseTestCase):

    fixtures = ['channel.json', 'lineup.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.schedule:lineup:make_draft_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(405, response.status_code)

    def test_wrong_id(self):
        self._login_user()
        for i in ['', 'non-int']:
            response = self.client.post('{0}?id={1}'.format(self.url, i))
            self.assertJsonError(response, 'UNEXPECTED_REQUEST_PARAMETER_VALUE')

    def test_404(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'REQUIRED_REQUEST_PARAMETER_IS_MISSING')
        response = self.client.post('{0}?id={1}'.format(self.url, 1000000))
        self.assertJsonError(response, 'LINEUP_NOT_FOUND')

    def test_draft(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.url, 2))
        self.assertJsonError(response, 'LINEUP_ALREADY_DRAFT')

    def test_normal(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.url, 1))
        self.assertJsonOk(response)
        prev_lineup = models.Lineup.objects.get(pk=3)
        lineup = models.Lineup.objects.get(pk=1)
        self.assertIsNone(prev_lineup.active_until)
        self.assertTrue(lineup.draft)
        self.assertIsNone(lineup.active_since)


class ProgramCreateJsonTestCase(LoginRequiredTestCase, JsonResponseTestCase):

    fixtures = ['program.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.schedule:program:create_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(405, response.status_code)

    def test_invalid_form(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'FORM_INVALID')

    def test_valid(self):
        self._login_user()
        response = self.client.post(
            self.url,
            {
                'name': 'Название тестовой программы',
                'lineup_size': '00:30:00',
                'max_duration': '00:27:00',
                'min_duration': '00:24:00',
                'description': 'Описание тестовой программы',
                'age_limit': '6',
                'color': '#ffffff'
            }
        )
        program_id = models.Program.objects.count()
        self.assertJsonOk(
            response,
            data=models.Program.objects.get(pk=program_id).get_absolute_url()
        )


class ProgramShowJsonTestCase(JsonResponseTestCase):

    fixtures = ['program.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.schedule:program:show_json')

    def test_wrong_id(self):
        for i in ['', 'non-int']:
            response = self.client.get('{0}?id={1}'.format(self.url, i))
            self.assertJsonError(response, 'UNEXPECTED_REQUEST_PARAMETER_VALUE')

    def test_404(self):
        response = self.client.get(self.url)
        self.assertJsonError(response, 'REQUIRED_REQUEST_PARAMETER_IS_MISSING')
        response = self.client.get('{0}?id={1}'.format(self.url, 1000000))
        self.assertJsonError(response, 'PROGRAM_NOT_FOUND')

    def test_normal(self):
        response = self.client.get('{0}?id={1}'.format(self.url, 1))
        self.assertJsonOk(response)
        for p in ['name', 'ls_hours', 'ls_minutes', 'age_limit']:
            self.assertIn(p, json.loads(response.content.decode())['data'])


class ProgramPositionShowJsonTestCase(JsonResponseTestCase):

    fixtures = ['lineup.json', 'channel.json', 'program.json', 'programposition.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.schedule:pp:show_json')

    def test_wrong_id(self):
        for i in ['', 'non-int']:
            response = self.client.get('{0}?id={1}'.format(self.url, i))
            self.assertJsonError(response, 'UNEXPECTED_REQUEST_PARAMETER_VALUE')

    def test_404(self):
        response = self.client.get(self.url)
        self.assertJsonError(response, 'REQUIRED_REQUEST_PARAMETER_IS_MISSING')
        response = self.client.get('{0}?id={1}'.format(self.url, 1000000))
        self.assertJsonError(response, 'PROGRAM_POSITION_NOT_FOUND')

    def test_normal(self):
        response = self.client.get('{0}?id={1}'.format(self.url, 1))
        self.assertJsonOk(response)
        for p in ['id', 'dow', 'start', 'end', 'comment', 'locked', 'program_id', 'program_name', 'program_url',
                  'program_ls', 'program_age_limit']:
            self.assertIn(p, json.loads(response.content.decode())['data'])


class ProgramPositionEditJsonTestCase(LoginRequiredTestCase, JsonResponseTestCase):

    fixtures = ['lineup.json', 'channel.json', 'program.json', 'programposition.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.schedule:pp:edit_json')

    def test_wrong_id(self):
        self._login_user()
        for i in ['', 'non-int']:
            response = self.client.get('{0}?id={1}'.format(self.url, i))
            self.assertJsonError(response, 'UNEXPECTED_REQUEST_PARAMETER_VALUE')

    def test_404(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertJsonError(response, 'REQUIRED_REQUEST_PARAMETER_IS_MISSING')
        response = self.client.get('{0}?id={1}'.format(self.url, 1000000))
        self.assertJsonError(response, 'PROGRAM_POSITION_NOT_FOUND')

    def test_normal(self):
        self._login_user()
        response = self.client.get('{0}?id={1}'.format(self.url, 30))
        self.assertJsonOk(response)
        json_data = json.loads(response.content.decode())['data']
        for p in ['id', 'dow', 'start_hours', 'start_minutes', 'end_hours', 'end_minutes', 'comment', 'locked',
                  'similar_pps_dow', 'program_id']:
            self.assertIn(p, json_data)
        self.assertEqual([5, 6], sorted(json_data['similar_pps_dow']))


class ProgramPositionDeleteJsonTestCase(LoginRequiredTestCase, JsonResponseTestCase):

    fixtures = ['lineup.json', 'channel.json', 'program.json', 'programposition.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.schedule:pp:delete_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(405, response.status_code)

    def test_wrong_id(self):
        self._login_user()
        for i in ['', 'non-int']:
            response = self.client.post('{0}?id={1}'.format(self.url, i))
            self.assertJsonError(response, 'UNEXPECTED_REQUEST_PARAMETER_VALUE')

    def test_404(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'REQUIRED_REQUEST_PARAMETER_IS_MISSING')
        response = self.client.post('{0}?id={1}'.format(self.url, 1000000))
        self.assertJsonError(response, 'PROGRAM_POSITION_NOT_FOUND')

    def test_edit_forbidden(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.url, 1))
        self.assertJsonError(response, 'LINEUP_EDIT_FORBIDDEN')

    def test_delete_empty(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.url, 34))
        self.assertJsonError(response, 'PROGRAM_POSITION_CANT_DELETE_EMPTY')

    def test_delete_repeat_invalid(self):
        self._login_user()
        response = self.client.post(
            '{0}?id={1}'.format(self.url, 32),
            {'r': 'invalid_repeat_data'}
        )
        self.assertJsonError(response, 'FORM_INVALID')

    def test_delete_single_expand_previous(self):
        self._login_user()
        pps = [(61, 60), (39, 38)]
        for pp_id, prev_pp_id in pps:
            pp_end_time = models.ProgramPosition.objects.get(pk=pp_id).end_time
            response = self.client.post('{0}?id={1}'.format(self.url, pp_id))
            self.assertJsonOk(response)
            with self.assertRaises(models.ProgramPosition.DoesNotExist):
                models.ProgramPosition.objects.get(pk=pp_id)
            self.assertEqual(pp_end_time, models.ProgramPosition.objects.get(pk=prev_pp_id).end_time)
        call_command('loaddata', 'programposition.json', verbosity=0)

    def test_delete_single_expand_next(self):
        self._login_user()
        pps = [(70, 60), (48, 49)]
        for pp_id, next_pp_id in pps:
            pp_start_time = models.ProgramPosition.objects.get(pk=pp_id).start_time
            response = self.client.post('{0}?id={1}'.format(self.url, pp_id))
            self.assertJsonOk(response)
            with self.assertRaises(models.ProgramPosition.DoesNotExist):
                models.ProgramPosition.objects.get(pk=pp_id)
            self.assertEqual(pp_start_time, models.ProgramPosition.objects.get(pk=next_pp_id).start_time)
        call_command('loaddata', 'programposition.json', verbosity=0)

    def test_delete_single_merge_empty(self):
        self._login_user()
        pp_id = 56
        previous_pp_id = 55
        next_pp_id = 57
        next_pp_end_time = models.ProgramPosition.objects.get(pk=next_pp_id).end_time
        response = self.client.post('{0}?id={1}'.format(self.url, pp_id))
        self.assertJsonOk(response)
        for i in [pp_id, next_pp_id]:
            with self.assertRaises(models.ProgramPosition.DoesNotExist):
                models.ProgramPosition.objects.get(pk=i)
        self.assertEqual(next_pp_end_time, models.ProgramPosition.objects.get(pk=previous_pp_id).end_time)
        call_command('loaddata', 'programposition.json', verbosity=0)

    def test_delete_single_make_empty(self):
        self._login_user()
        pp_id = 51
        response = self.client.post('{0}?id={1}'.format(self.url, pp_id))
        self.assertJsonOk(response)
        self.assertIsNone(models.ProgramPosition.objects.get(pk=pp_id).program)
        call_command('loaddata', 'programposition.json', verbosity=0)

    def test_delete_repeat(self):
        self._login_user()
        response = self.client.post(
            '{0}?id={1}'.format(self.url, 44),
            {'r': '5'}
        )
        self.assertJsonOk(response)
        with self.assertRaises(models.ProgramPosition.DoesNotExist):
            models.ProgramPosition.objects.get(pk=44)
        with self.assertRaises(models.ProgramPosition.DoesNotExist):
            models.ProgramPosition.objects.get(pk=53)
        self.assertEqual(5, models.ProgramPosition.objects.get(pk=58).program_id)
        call_command('loaddata', 'programposition.json', verbosity=0)


class ProgramPositionUpdateJsonTestCase(LoginRequiredTestCase, JsonResponseTestCase):

    fixtures = ['lineup.json', 'channel.json', 'program.json', 'programposition.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.schedule:pp:update_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(405, response.status_code)

    def test_wrong_id(self):
        self._login_user()
        for i in ['', 'non-int']:
            response = self.client.post('{0}?id={1}'.format(self.url, i))
            self.assertJsonError(response, 'UNEXPECTED_REQUEST_PARAMETER_VALUE')

    def test_404(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'REQUIRED_REQUEST_PARAMETER_IS_MISSING')
        response = self.client.post('{0}?id={1}'.format(self.url, 1000000))
        self.assertJsonError(response, 'PROGRAM_POSITION_NOT_FOUND')

    def test_edit_forbidden(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.url, 1))
        self.assertJsonError(response, 'LINEUP_EDIT_FORBIDDEN')

    def test_form_invalid(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.url, 32))
        self.assertJsonError(response, 'FORM_INVALID')

    def test_model_invalid(self):
        self._login_user()
        data = {
            'st_m': 0,
            'et_m': 0,
            'c': '',
            'l': False,
            'p': 1
        }
        test_data = [
            (71, 7, 7), (71, 8, 7), (71, 5, 7), (71, 20, 23),  # без перехода через полночь
            (78, 19, 19), (78, 17, 19), (78, 5, 7), (78, 22, 20),  # с переходом через полночь
            (85, 5, 7), (85, 5, 4), (85, 8, 7), (85, 5, 5),  # круглосуточная
        ]
        for d in test_data:
            data['st_h'] = d[1]
            data['et_h'] = d[2]
            response = self.client.post('{0}?id={1}'.format(self.url, d[0]), data)
            self.assertJsonError(response, 'MODEL_INVALID')

    def test_resize_empty(self):
        self._login_user()
        response = self.client.post(
            '{0}?id={1}'.format(self.url, 85),
            {
                'st_h': 8,
                'st_m': 0,
                'et_h': 4,
                'et_m': 0,
                'c': '',
                'l': False,
                'p': ''
            }
        )
        self.assertJsonError(response, 'PROGRAM_POSITION_CANT_RESIZE_EMPTY')

    def test_out_of_bounds(self):
        self._login_user()
        data = {
            'st_m': 0,
            'et_m': 0,
            'c': '',
            'l': False,
            'p': 1
        }
        test_data = [
            (92, 11, 18), (92, 11, 19), (92, 11, 17), (92, 12, 19), (92, 13, 19),  # без перехода через полночь
            (94, 21, 2), (94, 21, 3), (94, 21, 1), (94, 22, 3), (94, 23, 3),  # с переходом через полночь
        ]
        for d in test_data:
            data['st_h'] = d[1]
            data['et_h'] = d[2]
            response = self.client.post('{0}?id={1}'.format(self.url, d[0]), data)
            self.assertJsonError(response, 'PROGRAM_POSITION_NEW_OUT_OF_OLD_BOUNDS')

    def test_normal_expand_previous(self):
        self._login_user()
        response = self.client.post(
            '{0}?id={1}'.format(self.url, 92),
            {
                'st_h': 14,
                'st_m': 0,
                'et_h': 18,
                'et_m': 0,
                'c': '',
                'l': False,
                'p': 1
            }
        )
        self.assertJsonOk(response)
        self.assertEqual(14, models.ProgramPosition.objects.get(pk=92).start_time.hour)
        self.assertEqual(14, models.ProgramPosition.objects.get(pk=72).end_time.hour)

    def test_normal_expand_next(self):
        self._login_user()
        response = self.client.post(
            '{0}?id={1}'.format(self.url, 92),
            {
                'st_h': 12,
                'st_m': 0,
                'et_h': 16,
                'et_m': 0,
                'c': '',
                'l': False,
                'p': 1
            }
        )
        self.assertJsonOk(response)
        self.assertEqual(16, models.ProgramPosition.objects.get(pk=92).end_time.hour)
        self.assertEqual(16, models.ProgramPosition.objects.get(pk=93).start_time.hour)

    def test_normal_insert_before(self):
        self._login_user()
        response = self.client.post(
            '{0}?id={1}'.format(self.url, 51),
            {
                'st_h': 11,
                'st_m': 0,
                'et_h': 12,
                'et_m': 0,
                'c': '',
                'l': False,
                'p': 4
            }
        )
        self.assertJsonOk(response)
        new_start_time = models.ProgramPosition.objects.get(pk=51).start_time
        self.assertEqual(11, new_start_time.hour)
        self.assertEqual(
            10,
            models.ProgramPosition.objects.get(lineup_id=2, end_time=new_start_time, dow=5).start_time.hour
        )

    def test_normal_insert_after(self):
        self._login_user()
        response = self.client.post(
            '{0}?id={1}'.format(self.url, 61),
            {
                'st_h': 18,
                'st_m': 0,
                'et_h': 21,
                'et_m': 0,
                'c': '',
                'l': False,
                'p': 5
            }
        )
        self.assertJsonOk(response)
        new_end_time = models.ProgramPosition.objects.get(pk=61).end_time
        self.assertEqual(21, new_end_time.hour)
        self.assertEqual(
            22,
            models.ProgramPosition.objects.get(lineup_id=2, start_time=new_end_time, dow=7).end_time.hour
        )

    def test_normal_length_unchanged(self):
        self._login_user()
        response = self.client.post(
            '{0}?id={1}'.format(self.url, 39),
            {
                'st_h': 2,
                'st_m': 0,
                'et_h': 6,
                'et_m': 0,
                'c': '',
                'l': False,
                'p': 4
            }
        )
        self.assertJsonOk(response)
        self.assertEqual(4, models.ProgramPosition.objects.get(pk=39).program_id)


class ChannelShowLineupsTestCase(TestCase):

    fixtures = []

    def test_404(self):
        response = self.client.get(urlresolvers.reverse('efsw.schedule:channel:show_lineups', args=(1000000, )))
        self.assertEqual(404, response.status_code)


class ChannelEditTestCase(LoginRequiredTestCase):

    fixtures = []

    def test_404(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.schedule:channel:edit', args=(1000000, )))
        self.assertEqual(404, response.status_code)


class ChannelCreateJsonTestCase(LoginRequiredTestCase, JsonResponseTestCase):

    fixtures = ['channel.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.schedule:channel:create_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(405, response.status_code)

    def test_invalid(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'FORM_INVALID')

    def test_normal(self):
        self._login_user()
        response = self.client.post(
            self.url,
            {
                'name': 'Название для нового канала'
            }
        )
        self.assertJsonOk(response)
        self.assertEqual(
            'Название для нового канала',
            models.Channel.objects.get(pk=models.Channel.objects.count()).name
        )


class ChannelUpdateJsonTestCase(LoginRequiredTestCase, JsonResponseTestCase):

    fixtures = ['channel.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.schedule:channel:update_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(405, response.status_code)

    def test_wrong_id(self):
        self._login_user()
        for i in ['', 'non-int']:
            response = self.client.post('{0}?id={1}'.format(self.url, i))
            self.assertJsonError(response, 'UNEXPECTED_REQUEST_PARAMETER_VALUE')

    def test_404(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'REQUIRED_REQUEST_PARAMETER_IS_MISSING')
        response = self.client.post('{0}?id={1}'.format(self.url, 1000000))
        self.assertJsonError(response, 'CHANNEL_NOT_FOUND')

    def test_invalid(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'REQUIRED_REQUEST_PARAMETER_IS_MISSING')

    def test_normal(self):
        self._login_user()
        response = self.client.post(
            '{0}?id={1}'.format(self.url, 1),
            {
                'name': 'Обновлённое название для канала'
            }
        )
        self.assertJsonOk(response)
        self.assertEqual(
            'Обновлённое название для канала',
            models.Channel.objects.get(pk=1).name
        )


class ChannelActivateJsonTestCase(LoginRequiredTestCase, JsonResponseTestCase):

    fixtures = ['channel.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.schedule:channel:activate_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(405, response.status_code)

    def test_wrong_id(self):
        self._login_user()
        for i in ['', 'non-int']:
            response = self.client.post('{0}?id={1}'.format(self.url, i))
            self.assertJsonError(response, 'UNEXPECTED_REQUEST_PARAMETER_VALUE')

    def test_404(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'REQUIRED_REQUEST_PARAMETER_IS_MISSING')
        response = self.client.post('{0}?id={1}'.format(self.url, 1000000))
        self.assertJsonError(response, 'CHANNEL_NOT_FOUND')

    def test_already_active(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.url, 1))
        self.assertJsonError(response, 'CHANNEL_ALREADY_ACTIVE')

    def test_normal(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.url, 3))
        self.assertJsonOk(response)
        self.assertTrue(models.Channel.objects.get(pk=3).active)


class ChannelDeactivateJsonTestCase(LoginRequiredTestCase, JsonResponseTestCase):

    fixtures = ['channel.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = urlresolvers.reverse('efsw.schedule:channel:deactivate_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.url)
        self.assertEqual(405, response.status_code)

    def test_wrong_id(self):
        self._login_user()
        for i in ['', 'non-int']:
            response = self.client.post('{0}?id={1}'.format(self.url, i))
            self.assertJsonError(response, 'UNEXPECTED_REQUEST_PARAMETER_VALUE')

    def test_404(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'REQUIRED_REQUEST_PARAMETER_IS_MISSING')
        response = self.client.post('{0}?id={1}'.format(self.url, 1000000))
        self.assertJsonError(response, 'CHANNEL_NOT_FOUND')

    def test_already_active(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.url, 3))
        self.assertJsonError(response, 'CHANNEL_ALREADY_NOT_ACTIVE')

    def test_normal(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.url, 1))
        self.assertJsonOk(response)
        self.assertFalse(models.Channel.objects.get(pk=1).active)
