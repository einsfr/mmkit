from django.test import TestCase

from efsw.schedule import models, views


class MyTestCase(TestCase):

    fixtures = ['lineup.json', 'program.json', 'programposition.json']

    def test_function(self):
        print(views.get_lineup_table_data(models.Lineup.objects.get(pk=1)))