from django.core import urlresolvers

from efsw.common.utils.testcases import AbstractSecurityTestCase


class ScheduleSecurityTestCase(AbstractSecurityTestCase):

    fixtures = ['channel.json', 'lineup.json', 'program.json', 'programposition.json']

    def _get_login_path(self):
        return 'http://testserver/common/accounts/login/?next={0}'

    def _get_test_conditions(self):
        return [

            # ------------------------- Lineup -------------------------

            self.SecurityTestConditions(urlresolvers.reverse('efsw.schedule:lineup:list')),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.schedule:lineup:list_page', args=(1, ))),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:new'),
                anonymous=False,
                perm_codename='add_lineup'
            ),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.schedule:lineup:show_current')),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.schedule:lineup:show_current_channel', args=(1, ))),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:copy_part_modal'),
                anonymous=False,
                perm_codename='add_lineup'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:activate_part_modal'),
                anonymous=False,
                perm_codename='change_lineup'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:make_draft_part_modal'),
                anonymous=False,
                perm_codename='change_lineup'
            ),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.schedule:lineup:show', args=(1, ))),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:edit', args=(1, )),
                anonymous=False,
                perm_codename='change_lineup'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:edit_structure', args=(1, )),
                anonymous=False,
                perm_codename='change_lineup'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:edit_properties', args=(1, )),
                anonymous=False,
                perm_codename='change_lineup'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:show_part_pp_table_body', args=(1, ))
            ),

            # ------------------------- Lineup JSON -------------------------

            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:copy_json'),
                anonymous=False,
                perm_codename='add_lineup',
                method='post'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:activate_json'),
                anonymous=False,
                perm_codename='change_lineup',
                method='post'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:make_draft_json'),
                anonymous=False,
                perm_codename='change_lineup',
                method='post'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:create_json'),
                anonymous=False,
                perm_codename='add_lineup',
                method='post'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:update_json'),
                anonymous=False,
                perm_codename='change_lineup',
                method='post'
            ),

            # ------------------------- Program -------------------------

            self.SecurityTestConditions(urlresolvers.reverse('efsw.schedule:program:list')),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.schedule:program:list_page', args=(1, ))),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:program:new'),
                anonymous=False,
                perm_codename='add_program'
            ),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.schedule:program:show', args=(1, ))),

            # ------------------------- Program JSON -------------------------

            self.SecurityTestConditions(urlresolvers.reverse('efsw.schedule:program:show_json')),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:program:create_json'),
                anonymous=False,
                perm_codename='add_program',
                method='post'
            ),

            # ------------------------- ProgramPosition -------------------------

            self.SecurityTestConditions(urlresolvers.reverse('efsw.schedule:pp:show_part_modal')),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:pp:edit_part_modal'),
                anonymous=False,
                perm_codename='change_programposition'
            ),

            # ------------------------- ProgramPosition JSON -------------------------

            self.SecurityTestConditions(urlresolvers.reverse('efsw.schedule:pp:show_json')),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:pp:edit_json'),
                anonymous=False,
                perm_codename='change_programposition'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:pp:delete_json'),
                anonymous=False,
                perm_codename='change_programposition',
                method='post'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:pp:update_json'),
                anonymous=False,
                perm_codename='change_programposition',
                method='post'
            ),

            # ------------------------- Channel -------------------------

            self.SecurityTestConditions(urlresolvers.reverse('efsw.schedule:channel:list')),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.schedule:channel:list_page', args=(1, ))),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:channel:new'),
                anonymous=False,
                perm_codename='add_channel'
            ),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.schedule:channel:show_lineups', args=(1, ))),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.schedule:channel:show_lineups_page', args=(1, 2, ))),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:channel:edit', args=(1, )),
                anonymous=False,
                perm_codename='change_channel'
            ),

            # ------------------------- Channel JSON -------------------------

            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:channel:create_json'),
                anonymous=False,
                perm_codename='add_channel',
                method='post'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:channel:update_json'),
                anonymous=False,
                perm_codename='change_channel',
                method='post'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:channel:deactivate_json'),
                anonymous=False,
                perm_codename='change_channel',
                method='post'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:channel:activate_json'),
                anonymous=False,
                perm_codename='change_channel',
                method='post'
            ),

        ]

    def _get_app_label(self):
        return 'schedule'

    def test_security(self):
        self._test_admin_access()
        self._test_anonymous_access()
        self._test_concrete_permissions()
        self._test_non_priveleged_access()
