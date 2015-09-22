from efsw.conversion import views
from efsw.common.utils.testcases import UrlsTestCase


class ConversionUrlsTestCase(UrlsTestCase):

    def test_urls(self):
        urls = [

            ('efsw.conversion:task:list', [],
             '/conversion/tasks/list/', views.task_list),

            ('efsw.conversion:task:list_finished', [],
             '/conversion/tasks/list/finished/', views.task_list_finished),

            ('efsw.conversion:task:list_unknown', [],
             '/conversion/tasks/list/unknown/', views.task_list_unknown),

            ('efsw.conversion:task:list_in_progress', [],
             '/conversion/tasks/list/in_progress/', views.task_list_in_progress),

            ('efsw.conversion:task:list_enqueued', [],
             '/conversion/tasks/list/enqueued/', views.task_list_enqueued),

            ('efsw.conversion:task:new', [],
             '/conversion/tasks/new/', views.task_new),

            ('efsw.conversion:task:show', ['e0593092-fbc5-4b20-99f4-677f8954220f'],
             '/conversion/tasks/e0593092-fbc5-4b20-99f4-677f8954220f/show/', views.task_show),

            ('efsw.conversion:task:create_json', [],
             '/conversion/tasks/create/json/', views.task_create_json),

            ('efsw.conversion:profile:list', [],
             '/conversion/profiles/list/', views.profile_list),

            ('efsw.conversion:profile:list_page', [1],
             '/conversion/profiles/list/page/1/', views.profile_list),

            ('efsw.conversion:profile:new', [],
             '/conversion/profiles/new/', views.profile_new),

            ('efsw.conversion:profile:show', [1],
             '/conversion/profiles/1/show/', views.profile_show),

            ('efsw.conversion:profile:show_json', [],
             '/conversion/profiles/show/json/', views.profile_show_json),

            ('efsw.conversion:profile:create_json', [],
             '/conversion/profiles/create/json/', views.profile_create_json),

        ]
        self.process_urls(urls)
