from django.core import urlresolvers

from efsw.common.utils.testcases import AbstractSecurityTestCase, SecurityTestConditions


class ScheduleSecurityTestCase(AbstractSecurityTestCase):

    fixtures = ['channel.json', 'lineup.json', 'program.json', 'programposition.json']

    def _get_login_path(self):
        return 'http://testserver/common/accounts/login/?next={0}'

    def _get_test_conditions(self):
        return [

            # ------------------------- Lineup -------------------------

            SecurityTestConditions(urlresolvers.reverse('efsw.schedule:lineup:list')),
            SecurityTestConditions(urlresolvers.reverse('efsw.schedule:lineup:list_page', args=(1, ))),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:new'),
                anonymous=False,
                perm_codename='add_lineup'
            ),
            SecurityTestConditions(urlresolvers.reverse('efsw.schedule:lineup:show_current')),
            SecurityTestConditions(urlresolvers.reverse('efsw.schedule:lineup:show_current_channel', args=(1, ))),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:copy_part_modal'),
                anonymous=False,
                perm_codename='add_lineup'
            ),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:activate_part_modal'),
                anonymous=False,
                perm_codename='change_lineup'
            ),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:make_draft_part_modal'),
                anonymous=False,
                perm_codename='change_lineup'
            ),
            SecurityTestConditions(urlresolvers.reverse('efsw.schedule:lineup:show', args=(1, ))),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:edit', args=(1, )),
                anonymous=False,
                perm_codename='change_lineup'
            ),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:edit_structure', args=(1, )),
                anonymous=False,
                perm_codename='change_lineup'
            ),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:edit_properties', args=(1, )),
                anonymous=False,
                perm_codename='change_lineup'
            ),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:show_part_pp_table_body', args=(1, ))
            ),

            # ------------------------- Lineup JSON -------------------------

            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:copy_json'),
                anonymous=False,
                perm_codename='add_lineup',
                method='post'
            ),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:activate_json'),
                anonymous=False,
                perm_codename='change_lineup',
                method='post'
            ),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:make_draft_json'),
                anonymous=False,
                perm_codename='change_lineup',
                method='post'
            ),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:create_json'),
                anonymous=False,
                perm_codename='add_lineup',
                method='post'
            ),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:lineup:update_json'),
                anonymous=False,
                perm_codename='change_lineup',
                method='post'
            ),

            # ------------------------- Program -------------------------

            SecurityTestConditions(urlresolvers.reverse('efsw.schedule:program:list')),
            SecurityTestConditions(urlresolvers.reverse('efsw.schedule:program:list_page', args=(1, ))),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:program:new'),
                anonymous=False,
                perm_codename='add_program'
            ),
            SecurityTestConditions(urlresolvers.reverse('efsw.schedule:program:show', args=(1, ))),

            # ------------------------- Program JSON -------------------------

            SecurityTestConditions(urlresolvers.reverse('efsw.schedule:program:show_json')),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:program:create_json'),
                anonymous=False,
                perm_codename='add_program',
                method='post'
            ),

            # ------------------------- ProgramPosition -------------------------

            SecurityTestConditions(urlresolvers.reverse('efsw.schedule:pp:show_part_modal')),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:pp:edit_part_modal'),
                anonymous=False,
                perm_codename='change_programposition'
            ),

            # ------------------------- ProgramPosition JSON -------------------------

            SecurityTestConditions(urlresolvers.reverse('efsw.schedule:pp:show_json')),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:pp:edit_json'),
                anonymous=False,
                perm_codename='change_programposition'
            ),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:pp:delete_json'),
                anonymous=False,
                perm_codename='change_programposition',
                method='post'
            ),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:pp:update_json'),
                anonymous=False,
                perm_codename='change_programposition',
                method='post'
            ),

            # ------------------------- Channel -------------------------

            SecurityTestConditions(urlresolvers.reverse('efsw.schedule:channel:list')),
            SecurityTestConditions(urlresolvers.reverse('efsw.schedule:channel:list_page', args=(1, ))),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:channel:new'),
                anonymous=False,
                perm_codename='add_channel'
            ),
            SecurityTestConditions(urlresolvers.reverse('efsw.schedule:channel:show_lineups', args=(1, ))),
            SecurityTestConditions(urlresolvers.reverse('efsw.schedule:channel:show_lineups_page', args=(1, 2, ))),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:channel:edit', args=(1, )),
                anonymous=False,
                perm_codename='change_channel'
            ),

            # ------------------------- Channel JSON -------------------------

            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:channel:create_json'),
                anonymous=False,
                perm_codename='add_channel',
                method='post'
            ),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:channel:update_json'),
                anonymous=False,
                perm_codename='change_channel',
                method='post'
            ),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.schedule:channel:deactivate_json'),
                anonymous=False,
                perm_codename='change_channel',
                method='post'
            ),
            SecurityTestConditions(
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
