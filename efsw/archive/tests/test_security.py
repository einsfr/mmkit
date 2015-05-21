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
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:item:create_json'),
                anonymous=False,
                perm_codename='add_item',
                method='post'
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
                urlresolvers.reverse('efsw.archive:item:update', args=(1, )),
                anonymous=False,
                perm_codename='change_item',
                method='post'
            ),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:item:includes_list_json')),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:item:includes_check_json')),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:item:includes_update_json'),
                anonymous=False,
                perm_codename='change_item',
                method='post'
            ),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:item:locations_list_json')),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:item:locations_update_json'),
                anonymous=False,
                perm_codename='change_itemlocation',
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
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:category:create'),
                anonymous=False,
                perm_codename='add_itemcategory',
                method='post'
            ),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:category:items_list', args=(1, ))),
            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:category:items_list_page', args=(1, 1))),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:category:edit', args=(1, )),
                anonymous=False,
                perm_codename='change_itemcategory'
            ),
            self.SecurityTestConditions(
                urlresolvers.reverse('efsw.archive:category:update', args=(1, )),
                anonymous=False,
                perm_codename='change_itemcategory'
            ),
            # ------------------------- Storage -------------------------
            self.SecurityTestConditions(urlresolvers.reverse('efsw.archive:storage:show_json')),
        ]

    def test_security(self):
        self._test_admin_access()
        self._test_anonymous_access()
        self._test_concrete_permissions()
        self._test_non_priveleged_access()