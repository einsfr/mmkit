from efsw.archive import views
from efsw.common.utils.testcases import UrlsTestCase


class ArchiveUrlsTestCase(UrlsTestCase):

    def test_urls(self):
        urls = [

            # ------------------------- Item -------------------------

            ('efsw.archive:item:list', [],
             '/archive/items/list/', views.item_list),

            ('efsw.archive:item:list_page', [2],
             '/archive/items/list/page/2/', views.item_list),

            ('efsw.archive:item:new', [],
             '/archive/items/new/', views.item_new),

            ('efsw.archive:item:show', [12],
             '/archive/items/12/show/', views.item_show),

            ('efsw.archive:item:show_properties', [12],
             '/archive/items/12/show/properties/', views.item_show_properties),

            ('efsw.archive:item:show_locations', [12],
             '/archive/items/12/show/locations/', views.item_show_locations),

            ('efsw.archive:item:show_links', [12],
             '/archive/items/12/show/links/', views.item_show_links),

            ('efsw.archive:item:show_log', [12],
             '/archive/items/12/show/log/', views.item_show_log),

            ('efsw.archive:item:edit', [12],
             '/archive/items/12/edit/', views.item_edit),

            ('efsw.archive:item:edit_properties', [12],
             '/archive/items/12/edit/properties/', views.item_edit_properties),

            ('efsw.archive:item:edit_locations', [12],
             '/archive/items/12/edit/locations/', views.item_edit_locations),

            ('efsw.archive:item:edit_links', [12],
             '/archive/items/12/edit/links/', views.item_edit_links),

            # ------------------------- Item JSON -------------------------

            ('efsw.archive:item:check_links_json', [],
             '/archive/items/check/links/json/', views.item_check_links_json),

            ('efsw.archive:item:update_links_json', [],
             '/archive/items/update/links/json/', views.item_update_links_json),

            ('efsw.archive:item:show_locations_json', [],
             '/archive/items/show/locations/json/', views.item_show_locations_json),

            ('efsw.archive:item:update_locations_json', [],
             '/archive/items/update/locations/json/', views.item_update_locations_json),

            ('efsw.archive:item:create_json', [],
             '/archive/items/create/json/', views.item_create_json),

            ('efsw.archive:item:update_properties_json', [],
             '/archive/items/update/properties/json/', views.item_update_properties_json),

            # ------------------------- ItemCategory -------------------------

            ('efsw.archive:category:list', [],
             '/archive/categories/list/', views.category_list),

            ('efsw.archive:category:list_page', [2],
             '/archive/categories/list/page/2/', views.category_list),

            ('efsw.archive:category:new', [],
             '/archive/categories/new/', views.category_new),

            ('efsw.archive:category:show_items', [3],
             '/archive/categories/3/show/items/', views.category_show_items),

            ('efsw.archive:category:show_items_page', [3, 2],
             '/archive/categories/3/show/items/page/2/', views.category_show_items),

            ('efsw.archive:category:edit', [3],
             '/archive/categories/3/edit/', views.category_edit),

            # ------------------------- ItemCategory JSON -------------------------

            ('efsw.archive:category:create_json', [],
             '/archive/categories/create/json/', views.category_create_json),

            ('efsw.archive:category:update_json', [],
             '/archive/categories/update/json/', views.category_update_json),

            # ------------------------- Storage JSON -------------------------

            ('efsw.archive:storage:show_json', [],
             '/archive/storages/show/json/', views.storage_show_json),

            # ------------------------- Общие -------------------------

            ('efsw.archive:search', [],
             '/archive/search/', views.search)
        ]
        self.process_urls(urls)
