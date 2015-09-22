import json
import datetime

from django.test import TestCase
from django.core import urlresolvers, paginator

from mmkit.conf import settings
from efsw.conversion import models
from efsw.common.utils.testcases import LoginRequiredTestCase, JsonResponseTestCase


class TaskListTestCase(TestCase):

    fixtures = []

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
