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
        self.assertEqual(404, response.status_code)
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

# ------------------------- Lineup JSON -------------------------

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
        self.assertJsonError(response, 'lineup_not_found')

    def test_not_editable(self):
        self._login_user()
        response = self.client.post('{0}{1}'.format(self.url, '?id=1'))
        self.assertJsonError(response, 'lineup_edit_forbidden')

    def test_invalid(self):
        self._login_user()
        response = self.client.post(
            '{0}{1}'.format(self.url, '?id=2'),
            {'name': ''}
        )
        self.assertJsonError(response, 'form_invalid')

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

    fixtures = ['channel.json']

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
        self.assertJsonError(response, 'form_invalid')

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
            self.assertJsonError(response, 'id_not_int')

    def test_404(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'lineup_not_found')
        response = self.client.post('{0}?id={1}'.format(self.url, 1000000))
        self.assertJsonError(response, 'lineup_not_found')

    def test_invalid(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.url, 1))
        self.assertJsonError(response, 'form_invalid')

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
            self.assertJsonError(response, 'id_not_int')

    def test_404(self):
        self._login_user()
        response = self.client.post(self.url)
        self.assertJsonError(response, 'lineup_not_found')
        response = self.client.post('{0}?id={1}'.format(self.url, 1000000))
        self.assertJsonError(response, 'lineup_not_found')

    def test_non_draft(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.url, 1))
        self.assertJsonError(response, 'lineup_not_draft')

    def test_invalid(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.url, 2))
        self.assertJsonError(response, 'form_invalid')
