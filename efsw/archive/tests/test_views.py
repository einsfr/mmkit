import math
import json
import datetime

from django.test import TestCase
from django.core import urlresolvers
from django.core.management import call_command

from efsw.archive import models
from efsw.common.utils.testcases import LoginRequiredTestCase
from efsw.common.http.response import JsonWithStatusResponse


# ------------------------- Общие -------------------------


class SearchViewTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:search')

    def setUp(self):
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            call_command('esinit', replace=True, verbosity=2)
            call_command('esindex', 'archive.Item', verbosity=2)

    def test_disable_option(self):
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            response = self.client.get(self.request_url)
        self.assertContains(response, '<h2>Поиск по архиву</h2>', status_code=200)
        response = self.client.get(self.request_url)
        self.assertContains(response, 'Поиск не работает', status_code=500)

    def test_search_queries_q(self):
        get_data = {'q': 'новость'}
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            response = self.client.get(self.request_url, get_data)
        self.assertEqual(len(response.context['items']), 3)
        ids = [x.id for x in response.context['items']]
        self.assertIn(4, ids)
        self.assertIn(8, ids)

    def test_search_queries_qo(self):
        get_data = {'q': 'новость', 'o': '1'}
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            response = self.client.get(self.request_url, get_data)
        items = response.context['items']
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].id, 11)
        self.assertEqual(items[1].id, 4)
        self.assertEqual(items[2].id, 8)

    def test_search_queries_qc(self):
        get_data = {'q': 'новость', 'c': 1}
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            response = self.client.get(self.request_url, get_data)
        items = response.context['items']
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].id, 4)


# ------------------------- Item -------------------------


class ItemListViewTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def test_list(self):
        items_count = models.Item.objects.count()
        with self.settings(EFSW_ARCH_ITEM_LIST_PER_PAGE=1000):
            response = self.client.get(urlresolvers.reverse('efsw.archive:item:list'))
            self.assertContains(response, '<h2>Список элементов</h2>', status_code=200)
            self.assertEqual(items_count, len(response.context['items']))
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')

    def test_pagination(self):
        items_count = models.Item.objects.count()
        with self.settings(EFSW_ARCH_ITEM_LIST_PER_PAGE=1000):
            response = self.client.get(urlresolvers.reverse('efsw.archive:item:list_page', args=(2, )))
            self.assertContains(response, '<h2>Список элементов</h2>', status_code=200)
            self.assertEqual(items_count, len(response.context['items']))
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')
        with self.settings(EFSW_ARCH_ITEM_LIST_PER_PAGE=2):
            response = self.client.get(urlresolvers.reverse('efsw.archive:item:list_page', args=(1, )))
            self.assertContains(response, '<h2>Список элементов</h2>', status_code=200)
            self.assertEqual(2, len(response.context['items']))
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')
            self.assertContains(response, '<a href="/archive/items/list/page/2/" title="Следующая страница">»</a>')
            self.assertContains(
                response,
                '<a href="/archive/items/list/page/{0}/" title="Последняя страница">{0}</a>'.format(
                    math.ceil(items_count / 2)
                )
            )
            response = self.client.get(urlresolvers.reverse('efsw.archive:item:list_page', args=(2, )))
            self.assertContains(response, '<h2>Список элементов</h2>', status_code=200)
            self.assertEqual(2, len(response.context['items']))
            self.assertContains(response, '<a href="/archive/items/list/page/1/" title="Предыдущая страница">«</a>')
            self.assertContains(response, '<a href="#" title="Страница 2">2</a>')
            self.assertContains(response, '<a href="/archive/items/list/page/3/" title="Следующая страница">»</a>')


class ItemNewViewTestCase(LoginRequiredTestCase):

    fixtures = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:item:new')

    def test_page(self):
        self._login_user()
        response = self.client.get(self.request_url)
        self.assertContains(response, '<h2>Создание элемента</h2>', status_code=200)

    def test_wrong_method(self):
        self._login_user()
        response = self.client.post(self.request_url)
        self.assertEqual(405, response.status_code)


class ItemCreateJsonViewTestCase(LoginRequiredTestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:item:create_json')

    def test_valid(self):
        self._login_user()
        post_data = {
            'name': 'Новый элемент',
            'description': 'Описание нового элемента',
            'created': '2015-02-09',
            'author': 'Автор нового элемента',
            'category': '3',
        }
        response = self.client.post(self.request_url, post_data, follow=True)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_OK, json_content['status'])
        item_id = models.Item.objects.count()
        self.assertEqual('/archive/items/{0}/edit/locations/'.format(item_id), json_content['data'])
        response = self.client.get(json_content['data'])
        item = models.Item.objects.get(pk=response.context['item'].id)
        self.assertEqual('Новый элемент', item.name)
        self.assertEqual('Описание нового элемента', item.description)
        self.assertEqual('Автор нового элемента', item.author)
        self.assertEqual(datetime.date(2015, 2, 9), item.created)
        self.assertEqual(3, item.category.id)
        log = response.context['item'].log.all()
        self.assertEqual(1, len(log))
        self.assertEqual(log[0].ACTION_ADD, log[0].action)

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.request_url)
        self.assertEqual(405, response.status_code)

    def test_required_field(self):
        self._login_user()
        response = self.client.post(self.request_url)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        for field in ['name', 'description', 'created', 'author', 'category']:
            self.assertEqual(json.loads(json_content['data']['errors'])[field][0]['code'], 'required')

    def test_name_max_length(self):
        self._login_user()
        post_data = {
            'name': 'a' * 256,
        }
        response = self.client.post(self.request_url, post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual(json.loads(json_content['data']['errors'])['name'][0]['code'], 'max_length')

    def test_created_not_date(self):
        self._login_user()
        post_data = {
            'created': 'this-is-not-a-date',
        }
        response = self.client.post(self.request_url, post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual(json.loads(json_content['data']['errors'])['created'][0]['code'], 'invalid')

    def test_author_max_length(self):
        self._login_user()
        post_data = {
            'author': 'a' * 256,
        }
        response = self.client.post(self.request_url, post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual(json.loads(json_content['data']['errors'])['author'][0]['code'], 'max_length')

    def test_non_existent_category(self):
        self._login_user()
        post_data = {
            'category': 'non-existent-category',
        }
        response = self.client.post(self.request_url, post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual(json.loads(json_content['data']['errors'])['category'][0]['code'], 'invalid_choice')


class ItemShowPropertiesTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def test_nonexist(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show_properties', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

    def test_show_properties(self):
        item = models.Item.objects.get(pk=4)
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show_properties', args=(4, )))
        self.assertContains(response, item.name, status_code=200)
        self.assertContains(response, 'Описание элемента - Свойства')


class ItemShowLocationsTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def test_nonexist(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show_locations', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

    def test_show_locations(self):
        item = models.Item.objects.get(pk=4)
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show_locations', args=(4, )))
        self.assertContains(response, item.name, status_code=200)
        self.assertContains(response, 'Описание элемента - Размещение')


class ItemShowLinksTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def test_nonexist(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show_links', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

    def test_show_links(self):
        item = models.Item.objects.get(pk=4)
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show_links', args=(4, )))
        self.assertContains(response, item.name, status_code=200)
        self.assertContains(response, 'Описание элемента - Связи')


class ItemShowLogTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def test_nonexist(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show_log', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

    def test_show_log(self):
        item = models.Item.objects.get(pk=4)
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show_log', args=(4, )))
        self.assertContains(response, item.name, status_code=200)
        self.assertContains(response, 'Описание элемента - Журнал')


class ItemCheckLinksJsonTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:item:check_links_json')

    def test_wrong_type(self):
        response = self.client.get('{0}?id={1}&include_id={2}'.format(self.request_url, 1, 2))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('link_type_is_missed', json_content['status_ext'])
        response = self.client.get('{0}?id={1}&include_id={2}&type={3}'.format(self.request_url, 1, 2, 'non-int'))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('unknown_link_type', json_content['status_ext'])
        response = self.client.get('{0}?id={1}&include_id={2}&type={3}'.format(self.request_url, 1, 2, 3))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('unknown_link_type', json_content['status_ext'])

    def test_include_self(self):
        response = self.client.get('{0}?id={1}&include_id={2}&type={3}'.format(self.request_url, 4, 4, 2))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('self_self_link', json_content['status_ext'])

    def test_include_non_int(self):
        response = self.client.get('{0}?id={1}&include_id={2}&type={3}'.format(self.request_url, 'non-int', 3, 2))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('id_not_int', json_content['status_ext'])
        response = self.client.get('{0}?id={1}&include_id={2}&type={3}'.format(self.request_url, 4, 'non-int', 2))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('id_not_int', json_content['status_ext'])

    def test_id_not_set(self):
        response = self.client.get('{0}?id={1}&type={2}'.format(self.request_url, 1, 2))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('Проверьте строку запроса - возможно, не установлен один из параметров id или inc_id.', json_content['data'])
        response = self.client.get('{0}?include_id={1}&type={2}'.format(self.request_url, 1, 2))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('id_is_missed', json_content['status_ext'])

    def test_nonexist_item(self):
        response = self.client.get('{0}?id={1}&include_id={2}&type={3}'.format(self.request_url, 1000000, 8, 2))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('item_not_found', json_content['status_ext'])

    def test_nonexist_include(self):
        response = self.client.get('{0}?id={1}&include_id={2}&type={3}'.format(self.request_url, 4, 1000000, 2))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('item_not_found', json_content['status_ext'])

    def test_normal(self):
        response = self.client.get('{0}?id={1}&include_id={2}&type={3}'.format(self.request_url, 4, 8, 2))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_OK, json_content['status'])
        self.assertEqual(3, len(json_content['data']))
        self.assertIn('id', json_content['data'])
        self.assertIn('name', json_content['data'])
        self.assertIn('url', json_content['data'])


class ItemUpdateLinksJsonTestCase(LoginRequiredTestCase):

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:item:update_links_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.request_url)
        self.assertEqual(405, response.status_code)

    def test_nonexist_item(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.request_url, 1000000))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('item_not_found', json_content['status_ext'])

    def test_wrong_id(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.request_url, 'not-int'))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('id_not_int', json_content['status_ext'])

    def test_wrong_format(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.request_url, 4))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('wrong_format', json_content['status_ext'])
        post_data = {
            'includes': 'not-a-json-list',
            'included_in': 'not-a-json-list'
        }
        response = self.client.post('{0}?id={1}'.format(self.request_url, 4), post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('wrong_format', json_content['status_ext'])

    def test_clear(self):
        self._login_user()
        post_data = {
            'includes': '[]',
            'included_in': '[]',
        }
        response = self.client.post('{0}?id={1}'.format(self.request_url, 4), post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_OK, json_content['status'])
        self.assertEqual('', json_content['data'])
        item = models.Item.objects.get(pk=4)
        self.assertEqual([], list(item.includes.all()))
        self.assertEqual([], list(item.included_in.all()))
        logs = list(item.log.all().order_by('-pk'))
        self.assertEqual(2, len(logs))
        self.assertEqual(models.ItemLog.ACTION_INCLUDE_UPDATE, logs[0].action)
        logs = models.Item.objects.get(pk=5).log.all().order_by('-pk')
        self.assertEqual(3, len(logs))
        self.assertEqual(models.ItemLog.ACTION_INCLUDE_UPDATE, logs[0].action)
        logs = models.Item.objects.get(pk=11).log.all().order_by('-pk')
        self.assertEqual(1, len(logs))
        self.assertEqual(models.ItemLog.ACTION_INCLUDE_UPDATE, logs[0].action)
        call_command('loaddata', 'item.json', 'itemlog.json', verbosity=0)

    def test_normal(self):
        self._login_user()
        post_data = {
            'includes': '[4, 5, 8]',
            'included_in': '[10]',
        }
        response = self.client.post('{0}?id={1}'.format(self.request_url, 4), post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_OK, json_content['status'])
        self.assertEqual('', json_content['data'])
        item = models.Item.objects.get(pk=4)
        self.assertEqual([5, 8], [i.id for i in item.includes.all()])
        self.assertEqual([10], [i.id for i in item.included_in.all()])
        logs = list(item.log.all().order_by('-pk'))
        self.assertEqual(2, len(logs))
        self.assertEqual(models.ItemLog.ACTION_INCLUDE_UPDATE, logs[0].action)
        logs = models.Item.objects.get(pk=5).log.all()
        self.assertEqual(2, len(logs))
        logs = models.Item.objects.get(pk=8).log.all().order_by('-pk')
        self.assertEqual(1, len(logs))
        self.assertEqual(models.ItemLog.ACTION_INCLUDE_UPDATE, logs[0].action)
        logs = models.Item.objects.get(pk=10).log.all().order_by('-pk')
        self.assertEqual(1, len(logs))
        self.assertEqual(models.ItemLog.ACTION_INCLUDE_UPDATE, logs[0].action)
        call_command('loaddata', 'item.json', 'itemlog.json', verbosity=0)


class ItemUpdateLocationsJsonTestCase(LoginRequiredTestCase):

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json', 'itemlocation.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:item:update_locations_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.request_url)
        self.assertEqual(405, response.status_code)

    def test_nonexist_item(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.request_url, 1000000))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('item_not_found', json_content['status_ext'])

    def test_wrong_format(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.request_url, 4))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('wrong_format', json_content['status_ext'])
        post_data = {
            'locations': 'not-a-json-list'
        }
        response = self.client.post('{0}?id={1}'.format(self.request_url, 4), post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('wrong_format', json_content['status_ext'])

    def test_remove_all(self):
        self._login_user()
        post_data = {
            'locations': '[]'
        }
        response = self.client.post('{0}?id={1}'.format(self.request_url, 4), post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_OK, json_content['status'])
        self.assertEqual('', json_content['data'])
        item = models.Item.objects.get(pk=4)
        self.assertEqual([], list(item.locations.all()))
        call_command('loaddata', 'itemlog.json', 'itemlocation.json', verbosity=0)

    def test_nonexist_storage(self):
        self._login_user()
        post_data = {
            'locations': json.dumps([
                {
                    'id': 0,
                    'storage_id': 1000000,
                    'location': 'location'
                }
            ])
        }
        response = self.client.post('{0}?id={1}'.format(self.request_url, 4), post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('storage_not_found', json_content['status_ext'])

    def test_already_in_storage(self):
        self._login_user()
        post_data = {
            'locations': json.dumps([
                {
                    'id': 4,
                    'storage_id': 1,
                    'location': '00/00/00/04'
                },
                {
                    'id': 0,
                    'storage_id': 1,
                    'location': '00/00/00/04'
                }
            ])
        }
        response = self.client.post('{0}?id={1}'.format(self.request_url, 4), post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('item_storage_twice', json_content['status_ext'])

    def test_normal(self):
        self._login_user()
        post_data = {
            'locations': json.dumps([
                {
                    'id': 4,
                    'storage_id': 1,
                    'location': '00/00/00/04'
                },
                {
                    'id': 0,
                    'storage_id': 2,
                    'location': '00/00/00/04'
                },
            ])
        }
        response = self.client.post('{0}?id={1}'.format(self.request_url, 4), post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_OK, json_content['status'])
        self.assertEqual('/archive/items/4/edit/links/', json_content['data'])
        item = models.Item.objects.get(pk=4)
        locations = list(item.locations.all().order_by('-pk'))
        self.assertEqual(2, len(locations))
        self.assertEqual(2, locations[0].storage.id)
        self.assertEqual('00/00/00/04', locations[0].location)
        call_command('loaddata', 'itemlog.json', 'itemlocation.json', verbosity=0)


class ItemEditTestCase(LoginRequiredTestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def test_page(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:edit', args=(4, )))
        self.assertContains(response, 'Редактирование элемента - Свойства', status_code=200)

    def test_nonexist(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:edit', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

    def test_wrong_method(self):
        self._login_user()
        response = self.client.post(urlresolvers.reverse('efsw.archive:item:edit', args=(4, )))
        self.assertEqual(405, response.status_code)


class ItemEditPropertiesTestCase(LoginRequiredTestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def test_page(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:edit', args=(4, )))
        self.assertContains(response, 'Редактирование элемента - Свойства', status_code=200)

    def test_nonexist(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:edit', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

    def test_wrong_method(self):
        self._login_user()
        response = self.client.post(urlresolvers.reverse('efsw.archive:item:edit', args=(4, )))
        self.assertEqual(405, response.status_code)


class ItemEditLocationsTestCase(LoginRequiredTestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def test_page(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:edit_locations', args=(4, )))
        self.assertContains(response, 'Редактирование элемента - Размещение', status_code=200)

    def test_nonexist(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:edit_locations', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

    def test_wrong_method(self):
        self._login_user()
        response = self.client.post(urlresolvers.reverse('efsw.archive:item:edit_locations', args=(4, )))
        self.assertEqual(405, response.status_code)


class ItemEditLinksTestCase(LoginRequiredTestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def test_page(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:edit_links', args=(4, )))
        self.assertContains(response, 'Редактирование элемента - Связи', status_code=200)

    def test_nonexist(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:edit_links', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

    def test_wrong_method(self):
        self._login_user()
        response = self.client.post(urlresolvers.reverse('efsw.archive:item:edit_links', args=(4, )))
        self.assertEqual(405, response.status_code)


class ItemUpdatePropertiesJsonTestCase(LoginRequiredTestCase):

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json']

    def test_valid(self):
        self._login_user()
        post_data = {
            'name': 'Отредактированное название',
            'description': 'Отредактированное описание',
            'created': '2015-02-09',
            'author': 'Автор отредактированного элемента',
            'category': '1',
        }
        response = self.client.post(
            '{0}?id={1}'.format(
                urlresolvers.reverse('efsw.archive:item:update_properties_json'),
                4
            ),
            post_data
        )
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_OK, json_content['status'])
        self.assertEqual('/archive/items/4/edit/locations/', json_content['data'])
        item = models.Item.objects.get(pk=4)
        self.assertEqual('Отредактированное название', item.name)
        self.assertEqual('Отредактированное описание', item.description)
        self.assertEqual(datetime.date(2015, 2, 9), item.created)
        self.assertEqual('Автор отредактированного элемента', item.author)
        self.assertEqual(1, item.category.id)
        log = item.log.all()
        self.assertEqual(len(log), 2)
        self.assertEqual(log[0].action, log[0].ACTION_ADD)
        self.assertEqual(log[1].action, log[1].ACTION_UPDATE)

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get('{0}?id={1}'.format(
            urlresolvers.reverse('efsw.archive:item:update_properties_json'),
            4
        ))
        self.assertEqual(405, response.status_code)


class CategoryListTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def test_list(self):
        with self.settings(EFSW_ARCH_CATEGORY_LIST_PER_PAGE=1000):
            response = self.client.get(urlresolvers.reverse('efsw.archive:category:list'))
            self.assertContains(response, '<h2>Список категорий</h2>', status_code=200)
            self.assertEqual(models.ItemCategory.objects.count(), len(response.context['categories']))
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')

    def test_pagination(self):
        categories_count = models.ItemCategory.objects.count()
        with self.settings(EFSW_ARCH_CATEGORY_LIST_PER_PAGE=1000):
            response = self.client.get(urlresolvers.reverse('efsw.archive:category:list_page', args=(2, )))
            self.assertContains(response, '<h2>Список категорий</h2>', status_code=200)
            self.assertEqual(categories_count, len(response.context['categories']))
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')
        with self.settings(EFSW_ARCH_CATEGORY_LIST_PER_PAGE=2):
            response = self.client.get(urlresolvers.reverse('efsw.archive:category:list_page', args=(1, )))
            self.assertContains(response, '<h2>Список категорий</h2>', status_code=200)
            self.assertEqual(2, len(response.context['categories']))
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')
            self.assertContains(response, '<a href="/archive/categories/list/page/2/" title="Следующая страница">»</a>')
            response = self.client.get(urlresolvers.reverse('efsw.archive:category:list_page', args=(2, )))
            self.assertContains(response, '<h2>Список категорий</h2>', status_code=200)
            self.assertEqual(1, len(response.context['categories']))
            self.assertContains(response, '<a href="/archive/categories/list/page/1/" title="Предыдущая страница">«</a>')
            self.assertContains(response, '<a href="#" title="Страница 2">2</a>')


class CategoryNewTestCase(LoginRequiredTestCase):

    fixtures = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:category:new')

    def test_view(self):
        self._login_user()
        response = self.client.get(self.request_url)
        self.assertContains(response, '<h2>Создание категории</h2>', status_code=200)

    def test_wrong_method(self):
        self._login_user()
        response = self.client.post(self.request_url)
        self.assertEqual(405, response.status_code)


class CategoryCreateJsonTestCase(LoginRequiredTestCase):

    fixtures = ['itemcategory.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:category:create_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.request_url)
        self.assertEqual(405, response.status_code)

    def test_valid(self):
        self._login_user()
        post_data = {
            'name': 'Новая категория'
        }
        response = self.client.post(self.request_url, post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_OK, json_content['status'])
        call_command('loaddata', 'itemcategory.json', verbosity=0)

    def test_duplicate(self):
        self._login_user()
        post_data = {
            'name': 'Новая категория'
        }
        self.client.post(self.request_url, post_data)
        response = self.client.post(self.request_url, post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual(json.loads(json_content['data']['errors'])['name'][0]['code'], 'unique')
        call_command('loaddata', 'itemcategory.json', verbosity=0)

    def test_name_max_length(self):
        self._login_user()
        post_data = {
            'name': 'a' * 65
        }
        response = self.client.post(self.request_url, post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual(json.loads(json_content['data']['errors'])['name'][0]['code'], 'max_length')


class CategoryShowItemsTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def test_nonexist(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:category:show_items', args=(1000000, )))
        self.assertEqual(404, response.status_code)

    def test_view(self):
        with self.settings(EFSW_ARCH_ITEM_LIST_PER_PAGE=1000):
            response = self.client.get(urlresolvers.reverse('efsw.archive:category:show_items', args=(3, )))
            self.assertContains(
                response,
                '<h2>Список элементов в категории &laquo;Смонтированные репортажи&raquo;</h2>',
                status_code=200
            )
            self.assertEqual(models.ItemCategory.objects.get(pk=3).items.count(), len(response.context['items']))
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')
        with self.settings(EFSW_ARCH_ITEM_LIST_PER_PAGE=2):
            response = self.client.get(urlresolvers.reverse('efsw.archive:category:show_items', args=(2, )))
            self.assertContains(
                response,
                '<h2>Список элементов в категории &laquo;Исходные материалы&raquo;</h2>',
                status_code=200
            )
            self.assertEqual(2, len(response.context['items']))
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')
            self.assertContains(
                response,
                '<a href="/archive/categories/2/show/items/page/2/" title="Следующая страница">»</a>'
            )
            response = self.client.get(urlresolvers.reverse('efsw.archive:category:show_items_page', args=(2, 2, )))
            self.assertContains(
                response,
                '<h2>Список элементов в категории &laquo;Исходные материалы&raquo;</h2>',
                status_code=200
            )
            self.assertEqual(len(response.context['items']), 1)
            self.assertContains(response, '<a href="#" title="Страница 2">2</a>')
            self.assertContains(
                response,
                '<a href="/archive/categories/2/show/items/page/1/" title="Предыдущая страница">«</a>'
            )


class CategoryEditTestCase(LoginRequiredTestCase):

    fixtures = ['itemcategory.json']

    def test_wrong_method(self):
        self._login_user()
        response = self.client.post(urlresolvers.reverse('efsw.archive:category:edit', args=(3, )))
        self.assertEqual(405, response.status_code)

    def test_nonexist(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.archive:category:edit', args=(1000000, )))
        self.assertEqual(404, response.status_code)

    def test_normal(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.archive:category:edit', args=(3, )))
        self.assertEqual(200, response.status_code)


class CategoryUpdateJsonTestCase(LoginRequiredTestCase):

    fixtures = ['itemcategory.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:category:update_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get('{0}?id={1}'.format(self.request_url, 3))
        self.assertEqual(405, response.status_code)

    def test_nonexist(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.request_url, 1000000))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('category_not_found', json_content['status_ext'])

    def test_normal(self):
        self._login_user()
        post_data = {
            'name': 'Отредактированное название'
        }
        response = self.client.post('{0}?id={1}'.format(self.request_url, 3), post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_OK, json_content['status'])
        self.assertEqual('Отредактированное название', models.ItemCategory.objects.get(pk=3).name)
        call_command('loaddata', 'itemcategory.json', verbosity=0)


class StorageShowJsonTestCase(TestCase):

    fixtures = ['storage.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:storage:show_json')

    def test_nonexist(self):
        response = self.client.get('{0}?id={1}'.format(self.request_url, 1000000))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('storage_not_found', json_content['status_ext'])

    def test_normal(self):
        response = self.client.get('{0}?id={1}'.format(self.request_url, 1))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_OK, json_content['status'])
        storage_data = json_content['data']
        self.assertEqual(4, len(storage_data))
        for _ in ['id', 'name', 'disable_location', 'base_url']:
            self.assertIn(_, storage_data)
        self.assertEqual('Онлайн хранилище №1', storage_data['name'])
        self.assertTrue(storage_data['disable_location'])
        self.assertEqual('\\\\192.168.100.1\\', storage_data['base_url'])
