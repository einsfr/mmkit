from efsw.schedule import views
from efsw.common.utils.testcases import UrlsTestCase


class ScheduleUrlsTestCase(UrlsTestCase):

    def test_urls(self):
        urls = [

            # ------------------------- Lineup -------------------------

            ('efsw.schedule:lineup:list', [],
             '/schedule/lineups/list/', views.lineup_list),

            ('efsw.schedule:lineup:new', [],
             '/schedule/lineups/new/', views.lineup_new),

            ('efsw.schedule:lineup:list_page', [1],
             '/schedule/lineups/list/page/1/', views.lineup_list),

            ('efsw.schedule:lineup:show_current', [],
             '/schedule/lineups/show/current/', views.lineup_show_current),

            ('efsw.schedule:lineup:show_current_channel', [1],
             '/schedule/lineups/show/current/channel/1/', views.lineup_show_current),

            ('efsw.schedule:lineup:copy_part_modal', [],
             '/schedule/lineups/copy/part/modal/', views.lineup_copy_part_modal),

            ('efsw.schedule:lineup:activate_part_modal', [],
             '/schedule/lineups/activate/part/modal/', views.lineup_activate_part_modal),

            ('efsw.schedule:lineup:make_draft_part_modal', [],
             '/schedule/lineups/make_draft/part/modal/', views.lineup_make_draft_part_modal),

            ('efsw.schedule:lineup:show', [1],
             '/schedule/lineups/1/show/', views.lineup_show),

            ('efsw.schedule:lineup:edit', [1],
             '/schedule/lineups/1/edit/', views.lineup_edit),

            ('efsw.schedule:lineup:edit_structure', [1],
             '/schedule/lineups/1/edit/structure/', views.lineup_edit_structure),

            ('efsw.schedule:lineup:edit_properties', [1],
             '/schedule/lineups/1/edit/properties/', views.lineup_edit_properties),

            ('efsw.schedule:lineup:show_part_pp_table_body', [1],
             '/schedule/lineups/1/show/part/pp_table_body/', views.lineup_show_part_pp_table_body),

            # ------------------------- Lineup JSON -------------------------

            ('efsw.schedule:lineup:copy_json', [],
             '/schedule/lineups/copy/json/', views.lineup_copy_json),

            ('efsw.schedule:lineup:activate_json', [],
             '/schedule/lineups/activate/json/', views.lineup_activate_json),

            ('efsw.schedule:lineup:make_draft_json', [],
             '/schedule/lineups/make_draft/json/', views.lineup_make_draft_json),

            ('efsw.schedule:lineup:create_json', [],
             '/schedule/lineups/create/json/', views.lineup_create_json),

            ('efsw.schedule:lineup:update_json', [],
             '/schedule/lineups/update/json/', views.lineup_update_json),

            # ------------------------- Program -------------------------

            ('efsw.schedule:program:list', [],
             '/schedule/programs/list/', views.program_list),

            ('efsw.schedule:program:list_page', [1],
             '/schedule/programs/list/page/1/', views.program_list),

            ('efsw.schedule:program:new', [],
             '/schedule/programs/new/', views.program_new),

            ('efsw.schedule:program:show', [1],
             '/schedule/programs/1/show/', views.program_show),

            # ------------------------- Program JSON -------------------------

            ('efsw.schedule:program:show_json', [],
             '/schedule/programs/show/json/', views.program_show_json),

            ('efsw.schedule:program:create_json', [],
             '/schedule/programs/create/json/', views.program_create_json),

            # ------------------------- ProgramPosition -------------------------

            ('efsw.schedule:pp:show_part_modal', [],
             '/schedule/pps/show/part/modal/', views.pp_show_part_modal),

            ('efsw.schedule:pp:edit_part_modal', [],
             '/schedule/pps/edit/part/modal/', views.pp_edit_part_modal),

            # ------------------------- ProgramPosition JSON -------------------------

            ('efsw.schedule:pp:show_json', [],
             '/schedule/pps/show/json/', views.pp_show_json),

            ('efsw.schedule:pp:edit_json', [],
             '/schedule/pps/edit/json/', views.pp_edit_json),

            ('efsw.schedule:pp:delete_json', [],
             '/schedule/pps/delete/json/', views.pp_delete_json),

            ('efsw.schedule:pp:update_json', [],
             '/schedule/pps/update/json/', views.pp_update_json),

        ]
        self.process_urls(urls)
