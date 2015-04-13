from efsw.archive import views
from efsw.common.test.testcase import UrlsTestCase


class ArchiveUrlsTestCase(UrlsTestCase):

    def test_urls(self):
        urls = [
            ('efsw.archive:item:list', [],
             '/archive/items/list/', views.item_list),

            ('efsw.archive:item:list_page', [2],
             '/archive/items/list/page/2/', views.item_list),

            ('efsw.archive:item:new', [],
             '/archive/items/new/', views.item_new),

            ('efsw.archive:item:create', [],
             '/archive/items/create/', views.item_create),

            ('efsw.archive:item:show', [12],
             '/archive/items/12/show/', views.item_show),

            ('efsw.archive:item:logs_list', [12],
             '/archive/items/12/logs/list/', views.item_logs_list),

            ('efsw.archive:item:edit', [12],
             '/archive/items/12/edit/', views.item_edit),

            ('efsw.archive:item:update', [12],
             '/archive/items/12/update/', views.item_update),

            ('efsw.archive:item:includes_list_json', [],
             '/archive/items/includes/list/json/', views.item_includes_list_json),

            ('efsw.archive:item:includes_check_json', [],
             '/archive/items/includes/check/json/', views.item_includes_check_json),

            ('efsw.archive:item:includes_update_json', [],
             '/archive/items/includes/update/json/', views.item_includes_update_json),

            ('efsw.archive:item:locations_list_json', [],
             '/archive/items/locations/list/json/', views.item_locations_list_json),

            ('efsw.archive:item:locations_update_json', [],
             '/archive/items/locations/update/json/', views.item_locations_update_json),

            ('efsw.archive:category:list', [],
             '/archive/categories/list/', views.category_list),

            ('efsw.archive:category:new', [],
             '/archive/categories/new/', views.category_new),

            ('efsw.archive:category:create', [],
             '/archive/categories/create/', views.category_create),

            ('efsw.archive:category:items_list', [3],
             '/archive/categories/3/items/list/', views.category_items_list),

            ('efsw.archive:category:items_list_page', [3, 2],
             '/archive/categories/3/items/list/page/2/', views.category_items_list),

            ('efsw.archive:category:edit', [3],
             '/archive/categories/3/edit/', views.category_edit),

            ('efsw.archive:category:update', [3],
             '/archive/categories/3/update/', views.category_update),

            ('efsw.archive:storage:show_json', [],
             '/archive/storages/show/json/', views.storage_show_json),

            ('efsw.archive:search', [],
             '/archive/search/', views.search)
        ]
        self.process_urls(urls)