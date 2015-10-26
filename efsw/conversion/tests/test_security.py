from django.core import urlresolvers

from efsw.common.utils.testcases import AbstractSecurityTestCase, SecurityTestConditions
from efsw.conversion.fixtures import conversionprofile, conversiontask


class ConversionSecurityTestCase(AbstractSecurityTestCase):

    fixtures = []

    def _get_login_path(self):
        return 'http://testserver/accounts/login/?next={0}'

    def _get_test_conditions(self):
        return [

            SecurityTestConditions(urlresolvers.reverse('efsw.conversion:task:list')),
            SecurityTestConditions(urlresolvers.reverse('efsw.conversion:task:list_finished')),
            SecurityTestConditions(urlresolvers.reverse('efsw.conversion:task:list_unknown')),
            SecurityTestConditions(urlresolvers.reverse('efsw.conversion:task:list_in_progress')),
            SecurityTestConditions(urlresolvers.reverse('efsw.conversion:task:list_enqueued')),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.conversion:task:new'),
                anonymous=False,
                perm_codename='add_conversiontask'
            ),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.conversion:task:show', args=('e0593092-fbc5-4b20-99f4-677f8954220f', ))
            ),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.conversion:task:create_json'),
                anonymous=False,
                perm_codename='add_conversiontask',
                method='post'
            ),

            SecurityTestConditions(urlresolvers.reverse('efsw.conversion:profile:list')),
            SecurityTestConditions(urlresolvers.reverse('efsw.conversion:profile:list_page', args=(1, ))),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.conversion:profile:new'),
                anonymous=False,
                perm_codename='add_conversionprofile'
            ),
            SecurityTestConditions(urlresolvers.reverse('efsw.conversion:profile:show', args=(1, ))),
            SecurityTestConditions(urlresolvers.reverse('efsw.conversion:profile:show_json')),
            SecurityTestConditions(
                urlresolvers.reverse('efsw.conversion:profile:create_json'),
                anonymous=False,
                perm_codename='add_conversionprofile',
                method='post'
            )

        ]

    def _get_app_label(self):
        return 'conversion'

    def test_security(self):
        conversionprofile.load_data()
        conversiontask.load_data()
        self._test_admin_access()
        self._test_anonymous_access()
        self._test_concrete_permissions()
        self._test_non_priveleged_access()
