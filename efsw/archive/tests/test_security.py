from django.core import urlresolvers

from efsw.common.utils.testcases import AbstractSecurityTestCase


class ArchiveSecurityTestCase(AbstractSecurityTestCase):

    fixtures = ['item.json', 'itemcategory.json', 'storage.json', 'itemlog.json', 'itemlocation.json']

    def _get_login_path(self):
        return 'http://testserver/accounts/login/?next={0}'

    def _get_app_label(self):
        return 'archive'

    def _get_test_conditions(self):
        return [

            # ------------------------- Item -------------------------

            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:item:list')),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:item:list_page', args=(1, ))),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:item:new'),
                anonymous=False,
                perm_codename='add_item'
            ),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:item:show', args=(1,))),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:item:show_properties', args=(1,))),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:item:show_locations', args=(1,))),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:item:show_links', args=(1,))),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:item:show_log', args=(1,))),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:item:edit', args=(1, )),
                anonymous=False,
                perm_codename='change_item'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:item:edit_properties', args=(1, )),
                anonymous=False,
                perm_codename='change_item'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:item:edit_locations', args=(1, )),
                anonymous=False,
                perm_codename='change_item'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:item:edit_links', args=(1, )),
                anonymous=False,
                perm_codename='change_item'
            ),

            # ------------------------- Item JSON -------------------------

            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:item:check_links_json')),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:item:update_links_json'),
                anonymous=False,
                perm_codename='change_item',
                method='post'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:item:update_locations_json'),
                anonymous=False,
                perm_codename='change_itemlocation',
                method='post'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:item:create_json'),
                anonymous=False,
                perm_codename='add_item',
                method='post'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:item:update_properties_json'),
                anonymous=False,
                perm_codename='change_item',
                method='post'
            ),

            # ------------------------- ItemCategory -------------------------

            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:category:list')),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:category:list_page', args=(1, ))),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:category:new'),
                anonymous=False,
                perm_codename='add_itemcategory',
            ),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:category:show_items', args=(1, ))),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:category:show_items_page', args=(1, 1))),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:category:edit', args=(1, )),
                anonymous=False,
                perm_codename='change_itemcategory'
            ),

            # ------------------------- ItemCategory JSON -------------------------

            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:category:create_json'),
                anonymous=False,
                perm_codename='add_itemcategory',
                method='post'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:category:update_json'),
                anonymous=False,
                perm_codename='change_itemcategory',
                method='post'
            ),

            # ------------------------- Storage JSON -------------------------

            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:storage:show_json')),

            # ------------------------- Общие -------------------------

            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:search'),
                status_codes=[500]
            )
        ]

    def test_security(self):
        self._test_admin_access()
        self._test_anonymous_access()
        self._test_concrete_permissions()
        self._test_non_priveleged_access()