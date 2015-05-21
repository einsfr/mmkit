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
        self.assertContains(response, '<h1>Поиск по архиву</h1>', status_code=200)
        response = self.client.get(self.request_url)
        self.assertContains(response, '<h1>Поиск не работает</h1>', status_code=500)

    def test_search_queries_q(self):
        get_data = {'q': 'новость'}
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            response = self.client.get(self.request_url, get_data)
        self.assertContains(response, '<h2>Результаты поиска</h2>', status_code=200)
        self.assertEqual(len(response.context['items']), 2)
        ids = [x.id for x in response.context['items']]
        self.assertIn(4, ids)
        self.assertIn(8, ids)

    def test_search_queries_qo(self):
        get_data = {'q': 'новость', 'o': '1'}
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            response = self.client.get(self.request_url, get_data)
        self.assertContains(response, '<h2>Результаты поиска</h2>', status_code=200)
        items = response.context['items']
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].id, 4)
        self.assertEqual(items[1].id, 8)

    def test_search_queries_qc(self):
        get_data = {'q': 'новость', 'c': 1}
        with self.settings(EFSW_ELASTIC_DISABLE=False):
            response = self.client.get(self.request_url, get_data)
        self.assertContains(response, '<h2>Результаты поиска</h2>', status_code=200)
        items = response.context['items']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, 4)


# ------------------------- Item -------------------------


class ItemListViewTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def test_list(self):
        items_count = models.Item.objects.count()
        with self.settings(EFSW_ARCH_ITEM_LIST_PER_PAGE=1000):
            response = self.client.get(urlresolvers.reverse('efsw.archive:item:list'))
            self.assertContains(response, '<h1>Список элементов</h1>', status_code=200)
            self.assertEqual(items_count, len(response.context['items']))
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')

    def test_pagination(self):
        items_count = models.Item.objects.count()
        with self.settings(EFSW_ARCH_ITEM_LIST_PER_PAGE=1000):
            response = self.client.get(urlresolvers.reverse('efsw.archive:item:list_page', args=(2, )))
            self.assertContains(response, '<h1>Список элементов</h1>', status_code=200)
            self.assertEqual(items_count, len(response.context['items']))
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')
        with self.settings(EFSW_ARCH_ITEM_LIST_PER_PAGE=2):
            response = self.client.get(urlresolvers.reverse('efsw.archive:item:list_page', args=(1, )))
            self.assertContains(response, '<h1>Список элементов</h1>', status_code=200)
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
            self.assertContains(response, '<h1>Список элементов</h1>', status_code=200)
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
        self.assertContains(response, '<h1>Добавление нового элемента</h1>', status_code=200)

    def test_wrong_method(self):
        self._login_user()
        response = self.client.post(self.request_url)
        self.assertEqual(405, response.status_code)


class ItemCreateViewTestCase(LoginRequiredTestCase):

    fixtures = ['itemcategory.json']

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
        self.assertEqual('/archive/items/{0}/show/'.format(item_id), json_content['data'])
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


class ItemShowViewTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def test_nonexist(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show', args=(1000000, )))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show_properties', args=(1000000, )))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show_locations', args=(1000000, )))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show_links', args=(1000000, )))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show_log', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

    def test_show(self):
        item = models.Item.objects.get(pk=4)
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show', args=(4, )))
        self.assertContains(response, item.name, status_code=200)
        self.assertContains(response, 'Описание элемента - Свойства')

    def test_show_properties(self):
        item = models.Item.objects.get(pk=4)
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show_properties', args=(4, )))
        self.assertContains(response, item.name, status_code=200)
        self.assertContains(response, 'Описание элемента - Свойства')

    def test_show_locations(self):
        item = models.Item.objects.get(pk=4)
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show_locations', args=(4, )))
        self.assertContains(response, item.name, status_code=200)
        self.assertContains(response, 'Описание элемента - Размещение')

    def test_show_links(self):
        item = models.Item.objects.get(pk=4)
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show_links', args=(4, )))
        self.assertContains(response, item.name, status_code=200)
        self.assertContains(response, 'Описание элемента - Связи')

    def test_show_log(self):
        item = models.Item.objects.get(pk=4)
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show_log', args=(4, )))
        self.assertContains(response, item.name, status_code=200)
        self.assertContains(response, 'Описание элемента - Журнал')


class ItemIncludesListJsonTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:item:includes_list_json')

    def test_nonexist(self):
        response = self.client.get('{0}?id={1}'.format(self.request_url, 1000000))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('Ошибка: элемент с ID "1000000" не существует', json_content['data'])

    def test_normal(self):
        response = self.client.get('{0}?id={1}'.format(self.request_url, 4))
        self.assertIsInstance(response, JsonWithStatusResponse)
        item_includes = models.Item.objects.get(pk=4).includes.all()
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_OK, json_content['status'])
        id_list = []
        for d in json_content['data']:
            self.assertEqual(3, len(d))
            self.assertIn('id', d)
            self.assertIn('name', d)
            self.assertIn('url', d)
            id_list.append(d['id'])
        self.assertEqual(len(item_includes), len(json_content['data']))
        self.assertEqual(id_list, [i.id for i in item_includes])


class ItemIncludesCheckJsonTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:item:includes_check_json')

    def test_include_self(self):
        response = self.client.get('{0}?id={1}&include_id={2}'.format(self.request_url, 4, 4))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('Элемент не может быть включён сам в себя', json_content['data'])

    def test_include_non_int(self):
        response = self.client.get('{0}?id={1}&include_id={2}'.format(self.request_url, 'non-int', 4))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('Идентификатор должен быть целым числом', json_content['data'])
        response = self.client.get('{0}?id={1}&include_id={2}'.format(self.request_url, 4, 'non-int'))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('Идентификатор должен быть целым числом', json_content['data'])

    def test_id_not_set(self):
        response = self.client.get('{0}?id={1}'.format(self.request_url, 1))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('Проверьте строку запроса - возможно, не установлен id или include_id', json_content['data'])
        response = self.client.get('{0}?include_id={1}'.format(self.request_url, 1))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('Проверьте строку запроса - возможно, не установлен id или include_id', json_content['data'])

    def test_nonexist_item(self):
        response = self.client.get('{0}?id={1}&include_id={2}'.format(self.request_url, 1000000, 8))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('Ошибка: элемент с ID "1000000" не существует', json_content['data'])

    def test_nonexist_include(self):
        response = self.client.get('{0}?id={1}&include_id={2}'.format(self.request_url, 4, 1000000))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('Ошибка: элемент с ID "1000000" не существует', json_content['data'])

    def test_normal(self):
        response = self.client.get('{0}?id={1}&include_id={2}'.format(self.request_url, 4, 8))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_OK, json_content['status'])
        self.assertEqual(3, len(json_content['data']))
        self.assertIn('id', json_content['data'])
        self.assertIn('name', json_content['data'])
        self.assertIn('url', json_content['data'])


class ItemIncludesUpdateJsonTestCase(LoginRequiredTestCase):

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:item:includes_update_json')

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
        self.assertEqual('Ошибка: элемент с ID "1000000" не существует', json_content['data'])

    def test_wrong_format(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.request_url, 4))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('Неверный формат запроса', json_content['data'])
        post_data = {
            'includes': 'not-a-json-list'
        }
        response = self.client.post('{0}?id={1}'.format(self.request_url, 4), post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('Неверный формат запроса', json_content['data'])

    def test_clear(self):
        self._login_user()
        post_data = {
            'includes': '[]'
        }
        response = self.client.post('{0}?id={1}'.format(self.request_url, 4), post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_OK, json_content['status'])
        self.assertEqual('', json_content['data'])
        item = models.Item.objects.get(pk=4)
        self.assertEqual([], list(item.includes.all()))
        logs = list(item.log.all().order_by('-pk'))
        self.assertEqual(2, len(logs))
        self.assertEqual(models.ItemLog.ACTION_INCLUDE_UPDATE, logs[0].action)
        logs = models.Item.objects.get(pk=5).log.all().order_by('-pk')
        self.assertEqual(3, len(logs))
        self.assertEqual(models.ItemLog.ACTION_INCLUDE_UPDATE, logs[0].action)
        call_command('loaddata', 'item.json', 'itemlog.json', verbosity=0)

    def test_normal(self):
        self._login_user()
        post_data = {
            'includes': '[4, 5, 8]'
        }
        response = self.client.post('{0}?id={1}'.format(self.request_url, 4), post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_OK, json_content['status'])
        self.assertEqual('', json_content['data'])
        item = models.Item.objects.get(pk=4)
        self.assertEqual([5, 8], [i.id for i in item.includes.all()])
        logs = list(item.log.all().order_by('-pk'))
        self.assertEqual(2, len(logs))
        self.assertEqual(models.ItemLog.ACTION_INCLUDE_UPDATE, logs[0].action)
        logs = models.Item.objects.get(pk=5).log.all()
        self.assertEqual(2, len(logs))
        logs = models.Item.objects.get(pk=8).log.all().order_by('-pk')
        self.assertEqual(1, len(logs))
        self.assertEqual(models.ItemLog.ACTION_INCLUDE_UPDATE, logs[0].action)
        call_command('loaddata', 'item.json', 'itemlog.json', verbosity=0)


class ItemLocationsListJsonTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json', 'storage.json', 'itemlocation.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:item:locations_list_json')

    def test_nonexist(self):
        response = self.client.get('{0}?id={1}'.format(self.request_url, 1000000))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('Ошибка: элемент с ID "1000000" не существует', json_content['data'])

    def test_normal(self):
        response = self.client.get('{0}?id={1}'.format(self.request_url, 8))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_OK, json_content['status'])
        locations = json_content['data']
        self.assertEqual(2, len(locations))
        for l in locations:
            self.assertEqual(4, len(l))
            for _ in ['id', 'storage', 'storage_id', 'location']:
                self.assertIn(_, l)
        self.assertEqual([9, 10], sorted([l['id'] for l in locations]))


class ItemLocationsUpdateJsonTestCase(LoginRequiredTestCase):

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json', 'itemlocation.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:item:locations_update_json')

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
        self.assertEqual('Ошибка: элемент с ID "1000000" не существует', json_content['data'])

    def test_wrong_format(self):
        self._login_user()
        response = self.client.post('{0}?id={1}'.format(self.request_url, 4))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('Неверный формат запроса', json_content['data'])
        post_data = {
            'locations': 'not-a-json-list'
        }
        response = self.client.post('{0}?id={1}'.format(self.request_url, 4), post_data)
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('Неверный формат запроса', json_content['data'])

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
        self.assertEqual('Используется несуществующее хранилище', json_content['data'])

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
        self.assertEqual('Элемент не может иметь несколько расположений в одном хранилище', json_content['data'])

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
        self.assertEqual('', json_content['data'])
        item = models.Item.objects.get(pk=4)
        locations = list(item.locations.all().order_by('-pk'))
        self.assertEqual(2, len(locations))
        self.assertEqual(2, locations[0].storage.id)
        self.assertEqual('00/00/00/04', locations[0].location)
        call_command('loaddata', 'itemlog.json', 'itemlocation.json', verbosity=0)


class ItemEditViewTestCase(LoginRequiredTestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def test_page(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:edit', args=(4, )))
        self.assertContains(response, '<h1>Редактирование элемента</h1>', status_code=200)

    def test_nonexist(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:edit', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

    def test_wrong_method(self):
        self._login_user()
        response = self.client.post(urlresolvers.reverse('efsw.archive:item:edit', args=(4, )))
        self.assertEqual(405, response.status_code)


class ItemUpdateViewTestCase(LoginRequiredTestCase):

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
            urlresolvers.reverse('efsw.archive:item:update', args=(4, )),
            post_data,
            follow=True
        )
        self.assertEqual(1, len(response.redirect_chain))
        self.assertContains(response, 'Отредактированное название', status_code=200)
        item = models.Item.objects.get(pk=response.context['item'].id)
        self.assertEqual('Отредактированное название', item.name)
        self.assertEqual('Отредактированное описание', item.description)
        self.assertEqual(datetime.date(2015, 2, 9), item.created)
        self.assertEqual('Автор отредактированного элемента', item.author)
        self.assertEqual(1, item.category.id)
        log = response.context['item'].log.all()
        self.assertEqual(len(log), 2)
        self.assertEqual(log[0].action, log[0].ACTION_ADD)
        self.assertEqual(log[1].action, log[1].ACTION_UPDATE)

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:update', args=(4, )))
        self.assertEqual(405, response.status_code)


# ------------------------- ItemCategory -------------------------


class CategoryListViewTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def test_list(self):
        with self.settings(EFSW_ARCH_CATEGORY_LIST_PER_PAGE=1000):
            response = self.client.get(urlresolvers.reverse('efsw.archive:category:list'))
            self.assertContains(response, '<h1>Список категорий</h1>', status_code=200)
            self.assertEqual(models.ItemCategory.objects.count(), len(response.context['categories']))
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')

    def test_pagination(self):
        categories_count = models.ItemCategory.objects.count()
        with self.settings(EFSW_ARCH_CATEGORY_LIST_PER_PAGE=1000):
            response = self.client.get(urlresolvers.reverse('efsw.archive:category:list_page', args=(2, )))
            self.assertContains(response, '<h1>Список категорий</h1>', status_code=200)
            self.assertEqual(categories_count, len(response.context['categories']))
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')
        with self.settings(EFSW_ARCH_CATEGORY_LIST_PER_PAGE=2):
            response = self.client.get(urlresolvers.reverse('efsw.archive:category:list_page', args=(1, )))
            self.assertContains(response, '<h1>Список категорий</h1>', status_code=200)
            self.assertEqual(2, len(response.context['categories']))
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')
            self.assertContains(response, '<a href="/archive/categories/list/page/2/" title="Следующая страница">»</a>')
            response = self.client.get(urlresolvers.reverse('efsw.archive:category:list_page', args=(2, )))
            self.assertContains(response, '<h1>Список категорий</h1>', status_code=200)
            self.assertEqual(1, len(response.context['categories']))
            self.assertContains(response, '<a href="/archive/categories/list/page/1/" title="Предыдущая страница">«</a>')
            self.assertContains(response, '<a href="#" title="Страница 2">2</a>')


class CategoryNewViewTestCase(LoginRequiredTestCase):

    fixtures = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:category:new')

    def test_view(self):
        self._login_user()
        response = self.client.get(self.request_url)
        self.assertContains(response, '<h1>Добавление категории</h1>', status_code=200)

    def test_wrong_method(self):
        self._login_user()
        response = self.client.post(self.request_url)
        self.assertEqual(405, response.status_code)


class CategoryCreateViewTestCase(LoginRequiredTestCase):

    fixtures = ['itemcategory.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:category:create')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.request_url)
        self.assertEqual(405, response.status_code)

    def test_valid(self):
        self._login_user()
        post_data = {
            'name': 'Новая категория'
        }
        response = self.client.post(self.request_url, post_data, follow=True)
        self.assertContains(response, '<h1>Список категорий</h1>', status_code=200)
        self.assertEqual(1, len(response.redirect_chain))
        self.assertEqual(4, len(response.context['categories']))
        call_command('loaddata', 'itemcategory.json', verbosity=0)

    def test_duplicate(self):
        self._login_user()
        post_data = {
            'name': 'Новая категория'
        }
        self.client.post(self.request_url, post_data)
        response = self.client.post(self.request_url, post_data)
        self.assertContains(response, '<h1>Добавление категории</h1>', status_code=200)
        self.assertFormError(response, 'form', 'name', 'Категория с таким Название уже существует.')
        call_command('loaddata', 'itemcategory.json', verbosity=0)

    def test_name_max_length(self):
        self._login_user()
        post_data = {
            'name': 'a' * 65
        }
        response = self.client.post(self.request_url, post_data)
        self.assertContains(response, '<h1>Добавление категории</h1>', status_code=200)
        self.assertFormError(
            response,
            'form',
            'name',
            'Убедитесь, что это значение содержит не более 64 символов (сейчас 65).'
        )


class CategoryItemsListViewTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json']

    def test_nonexist(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:category:items_list', args=(1000000, )))
        self.assertEqual(404, response.status_code)

    def test_view(self):
        with self.settings(EFSW_ARCH_ITEM_LIST_PER_PAGE=1000):
            response = self.client.get(urlresolvers.reverse('efsw.archive:category:items_list', args=(3, )))
            self.assertContains(
                response,
                '<h1>Список элементов в категории &laquo;Смонтированные репортажи&raquo;</h1>',
                status_code=200
            )
            self.assertEqual(models.ItemCategory.objects.get(pk=3).items.count(), len(response.context['items']))
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')
        with self.settings(EFSW_ARCH_ITEM_LIST_PER_PAGE=2):
            response = self.client.get(urlresolvers.reverse('efsw.archive:category:items_list', args=(2, )))
            self.assertContains(
                response,
                '<h1>Список элементов в категории &laquo;Исходные материалы&raquo;</h1>',
                status_code=200
            )
            self.assertEqual(2, len(response.context['items']))
            self.assertContains(response, '<a href="#" title="Страница 1">1</a>')
            self.assertContains(
                response,
                '<a href="/archive/categories/2/items/list/page/2/" title="Следующая страница">»</a>'
            )
            response = self.client.get(urlresolvers.reverse('efsw.archive:category:items_list_page', args=(2, 2, )))
            self.assertContains(
                response,
                '<h1>Список элементов в категории &laquo;Исходные материалы&raquo;</h1>',
                status_code=200
            )
            self.assertEqual(len(response.context['items']), 1)
            self.assertContains(response, '<a href="#" title="Страница 2">2</a>')
            self.assertContains(
                response,
                '<a href="/archive/categories/2/items/list/page/1/" title="Предыдущая страница">«</a>'
            )


class CategoryEditViewTestCase(LoginRequiredTestCase):

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
        self.assertContains(response, '<h1>Редактирование категории</h1>', status_code=200)


class CategoryUpdateViewTestCase(LoginRequiredTestCase):

    fixtures = ['itemcategory.json']

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.archive:category:update', args=(3, )))
        self.assertEqual(405, response.status_code)

    def test_nonexist(self):
        self._login_user()
        response = self.client.post(urlresolvers.reverse('efsw.archive:category:update', args=(1000000, )))
        self.assertEqual(404, response.status_code)

    def test_normal(self):
        self._login_user()
        post_data = {
            'name': 'Отредактированное название'
        }
        response = self.client.post(
            urlresolvers.reverse('efsw.archive:category:update', args=(3, )),
            post_data,
            follow=True
        )
        self.assertContains(response, '<h1>Список категорий</h1>', status_code=200)
        self.assertEqual(1, len(response.redirect_chain))
        self.assertEqual('Отредактированное название', models.ItemCategory.objects.get(pk=3).name)
        call_command('loaddata', 'itemcategory.json', verbosity=0)


# ------------------------- Storage -------------------------


class StorageShowJsonViewTestCase(TestCase):

    fixtures = ['storage.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:storage:show_json')

    def test_nonexist(self):
        response = self.client.get('{0}?id={1}'.format(self.request_url, 1000000))
        self.assertIsInstance(response, JsonWithStatusResponse)
        json_content = json.loads(response.content.decode())
        self.assertEqual(JsonWithStatusResponse.STATUS_ERROR, json_content['status'])
        self.assertEqual('Ошибка: хранилище с ID "1000000" не существует', json_content['data'])

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