import math
import json

from django.test import TestCase
from django.core import urlresolvers
from django.core.management import call_command

from efsw.archive import models
from efsw.common.test.testcase import LoginRequiredTestCase
from efsw.common.http.response import JsonWithStatusResponse


class SearchViewTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json']

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


class ItemListViewTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json']

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

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json']

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

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:item:create')

    def test_valid(self):
        self._login_user()
        post_data = {
            'name': 'Новый элемент',
            'description': 'Описание нового элемента',
            'created': '2015-02-09',
            'author': 'Автор нового элемента',
            'storage': '1',
            'category': '3',
        }
        response = self.client.post(self.request_url, post_data, follow=True)
        self.assertEqual(1, len(response.redirect_chain))
        self.assertContains(response, '<h1>Описание элемента</h1>', status_code=200)
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
        self.assertEqual(response.status_code, 200)
        for field in ['name', 'description', 'created', 'author', 'category']:
            self.assertFormError(response, 'form', field, 'Обязательное поле.')

    def test_name_max_length(self):
        self._login_user()
        post_data = {
            'name': 'a' * 256,
        }
        response = self.client.post(self.request_url, post_data)
        self.assertFormError(
            response,
            'form',
            'name',
            'Убедитесь, что это значение содержит не более 255 символов (сейчас 256).'
        )

    def test_created_not_date(self):
        self._login_user()
        post_data = {
            'created': 'this-is-not-a-date',
        }
        response = self.client.post(self.request_url, post_data)
        self.assertFormError(
            response,
            'form',
            'created',
            'Введите правильную дату.'
        )

    def test_author_max_length(self):
        self._login_user()
        post_data = {
            'author': 'a' * 256,
        }
        response = self.client.post(self.request_url, post_data)
        self.assertFormError(
            response,
            'form',
            'author',
            'Убедитесь, что это значение содержит не более 255 символов (сейчас 256).'
        )

    def test_non_existent_category(self):
        self._login_user()
        post_data = {
            'category': 'non-existent-category',
        }
        response = self.client.post(self.request_url, post_data)
        self.assertFormError(
            response,
            'form',
            'category',
            'Выберите корректный вариант. Вашего варианта нет среди допустимых значений.'
        )


class ItemShowViewTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json']

    def test_nonexist(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

    def test_show(self):
        item = models.Item.objects.get(pk=4)
        includes_count = item.includes.count()
        log_count = item.log.count()
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:show', args=(4, )))
        self.assertContains(response, '<h1>Описание элемента</h1>', status_code=200)
        self.assertEqual(includes_count, len(response.context['item'].includes.all()))
        self.assertEqual(log_count, len(response.context['item'].log.all()))


class ItemIncludesListJsonTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json']

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

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json']

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


class ItemIncludesUpdateJsonTestCase(LoginRequiredTestCase):  # TODO: Доделать

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:item:includes_update_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.request_url)
        self.assertEqual(405, response.status_code)


class ItemLocationsListJsonTestCase(TestCase):  # TODO: Доделать

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json']


class ItemLocationsUpdateJsonTestCase(LoginRequiredTestCase):  # TODO: Доделать

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_url = urlresolvers.reverse('efsw.archive:item:locations_update_json')

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(self.request_url)
        self.assertEqual(405, response.status_code)


class ItemLogsListViewTestCase(TestCase):

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json']

    def test_nonexist(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:logs_list', args=(1000000, )))
        self.assertEqual(response.status_code, 404)

    def test_logs_list(self):
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:logs_list', args=(1, )))
        self.assertContains(response, '<h1>Журнал изменений элемента</h1>', status_code=200)


class ItemEditViewTestCase(LoginRequiredTestCase):

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json']

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

    fixtures = ['item.json', 'itemcategory.json', 'itemlog.json', 'storage.json']

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
        self.assertContains(response, '<h1>Описание элемента</h1>', status_code=200)
        log = response.context['item'].log.all()
        self.assertEqual(len(log), 2)
        self.assertEqual(log[0].action, log[0].ACTION_ADD)
        self.assertEqual(log[1].action, log[1].ACTION_UPDATE)

    def test_wrong_method(self):
        self._login_user()
        response = self.client.get(urlresolvers.reverse('efsw.archive:item:update', args=(4, )))
        self.assertEqual(405, response.status_code)