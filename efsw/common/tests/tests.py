from django.test import TestCase, override_settings
from django.core import paginator
from django.conf import settings

from efsw.common.templatetags import pagination
from efsw.common import default_settings


@override_settings(ROOT_URLCONF='efsw.common.tests.tests_urls')
class PaginationTagTestCase(TestCase):

    _next_page_text = getattr(settings, 'EFSW_COMM_PAGIN_NEXT_TEXT', default_settings.EFSW_COMM_PAGIN_NEXT_TEXT)

    _prev_page_text = getattr(settings, 'EFSW_COMM_PAGIN_PREV_TEXT', default_settings.EFSW_COMM_PAGIN_PREV_TEXT)

    def _test_prev_at(self, prep, pos, num, query_string):
        self.assertEqual(prep[pos]['text'], self._prev_page_text)
        self.assertEqual(prep[pos]['url'], '/page/{0}/{1}'.format(num, query_string))
        self.assertFalse(prep[pos]['active'])

    def _test_next_at(self, prep, pos, num, query_string):
        self.assertEqual(prep[pos]['text'], self._next_page_text)
        self.assertEqual(prep[pos]['url'], '/page/{0}/{1}'.format(num, query_string))
        self.assertFalse(prep[pos]['active'])

    def _test_active_num_at(self, prep, pos, num):
        self.assertEqual(prep[pos]['text'], str(num))
        self.assertEqual(prep[pos]['url'], '#')
        self.assertTrue(prep[pos]['active'])

    def _test_num_at(self, prep, pos_num_dict, query_string):
        for pos, num in pos_num_dict.items():
            self.assertEqual(prep[pos]['text'], str(num))
            self.assertEqual(prep[pos]['url'], '/page/{0}/{1}'.format(num, query_string))
            self.assertFalse(prep[pos]['active'])

    def _process_test_list(self, page_count, test_list, query_string=''):
        pagin = paginator.Paginator([x for x in range(1, page_count + 1)], 1)
        page_num = 1
        for test_string in test_list:
            page = pagin.page(page_num)
            prep = pagination._prepare(page, 'page', query_string)
            if query_string:
                query_string = '?{0}'.format(query_string)
            parts = test_string.split(' ')
            self.assertEqual(len(prep), len(parts))
            for num, p in enumerate(parts):
                if p[0] == '<' and p[-1] == '>':
                    self._test_active_num_at(prep, num, int(p[1:-1]))
                    active_page_number = int(p[1:-1])
            pos_num = {}
            for num, p in enumerate(parts):
                if p == self._prev_page_text:
                    self._test_prev_at(prep, num, active_page_number - 1, query_string)
                elif p == self._next_page_text:
                    self._test_next_at(prep, num, active_page_number + 1, query_string)
                elif p[0] != '<' and p[-1] != '>':
                    pos_num[num] = int(p)
            self._test_num_at(prep, pos_num, query_string)
            page_num += 1

    def test_pagination(self):
        """ Тесты для листалки """

        """
        ------ Всего страниц: 1, показывать соседей: 1 ------
        1: <1>
        """

        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            self._process_test_list(1, ['<1>'])

        """
        --- Всего страниц: 1, показывать соседей: 2 ---
        1: <1>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            self._process_test_list(1, ['<1>'])

        """
        --- Всего страниц: 1, показывать соседей: 20 ---
        1: <1>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            self._process_test_list(1, ['<1>'])

        """
        ------ Всего страниц: 2, показывать соседей: 1 ------
        1: <1> 2 >>
        2: << 1 <2>
        """

        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            self._process_test_list(2, ['<1> 2 >>', '<< 1 <2>'])

        """
        --- Всего страниц: 2, показывать соседей: 2 ---
        1: <1> 2 >>
        2: << 1 <2>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            self._process_test_list(2, ['<1> 2 >>', '<< 1 <2>'])

        """
        --- Всего страниц: 2, показывать соседей: 20 ---
        1: <1> 2 >>
        2: << 1 <2>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            self._process_test_list(2, ['<1> 2 >>', '<< 1 <2>'])

        """
        ------ Всего страниц: 3, показывать соседей: 1 ------
        1: <1> 2 >> 3
        2: << 1 <2> 3 >>
        3: 1 << 2 <3>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            self._process_test_list(3, ['<1> 2 >> 3', '<< 1 <2> 3 >>', '1 << 2 <3>'])

        """
        --- Всего страниц: 3, показывать соседей: 2 ---
        1: <1> 2 3 >>
        2: << 1 <2> 3 >>
        3: << 1 2 <3>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            self._process_test_list(3, ['<1> 2 3 >>', '<< 1 <2> 3 >>', '<< 1 2 <3>'])

        """
        --- Всего страниц: 3, показывать соседей: 20 ---
        1: <1> 2 3 >>
        2: << 1 <2> 3 >>
        3: << 1 2 <3>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            self._process_test_list(3, ['<1> 2 3 >>', '<< 1 <2> 3 >>', '<< 1 2 <3>'])

        """
        ------ Всего страниц: 4, показывать соседей: 1 ------
        1: <1> 2 >> 4
        2: << 1 <2> 3 >> 4
        3: 1 << 2 <3> 4 >>
        4: 1 << 3 <4>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            self._process_test_list(4, ['<1> 2 >> 4', '<< 1 <2> 3 >> 4', '1 << 2 <3> 4 >>', '1 << 3 <4>'])

        """
        --- Всего страниц: 4, показывать соседей: 2 ---
        1: <1> 2 3 >> 4
        2: << 1 <2> 3 4 >>
        3: << 1 2 <3> 4 >>
        4: 1 << 2 3 <4>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            self._process_test_list(4, ['<1> 2 3 >> 4', '<< 1 <2> 3 4 >>', '<< 1 2 <3> 4 >>', '1 << 2 3 <4>'])

        """
        --- Всего страниц: 4, показывать соседей: 20 ---
        1: <1> 2 3 4 >>
        2: << 1 <2> 3 4 >>
        3: << 1 2 <3> 4 >>
        4: << 1 2 3 <4>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            self._process_test_list(4, ['<1> 2 3 4 >>', '<< 1 <2> 3 4 >>', '<< 1 2 <3> 4 >>', '<< 1 2 3 <4>'])

        """
        ------ Всего страниц: 5, показывать соседей: 1 ------
        1: <1> 2 >> 5
        2: << 1 <2> 3 >> 5
        3: 1 << 2 <3> 4 >> 5
        4: 1 << 3 <4> 5 >>
        5: 1 << 4 <5>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            self._process_test_list(5, ['<1> 2 >> 5', '<< 1 <2> 3 >> 5', '1 << 2 <3> 4 >> 5', '1 << 3 <4> 5 >>',
                                    '1 << 4 <5>'])

        """
        --- Всего страниц: 5, показывать соседей: 2 ---
        1: <1> 2 3 >> 5
        2: << 1 <2> 3 4 >> 5
        3: << 1 2 <3> 4 5 >>
        4: 1 << 2 3 <4> 5 >>
        5: 1 << 3 4 <5>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            self._process_test_list(5, ['<1> 2 3 >> 5', '<< 1 <2> 3 4 >> 5', '<< 1 2 <3> 4 5 >>', '1 << 2 3 <4> 5 >>',
                                    '1 << 3 4 <5>'])

        """
        --- Всего страниц: 5, показывать соседей: 20 ---
        1: <1> 2 3 4 5 >>
        2: << 1 <2> 3 4 5 >>
        3: << 1 2 <3> 4 5 >>
        4: << 1 2 3 <4> 5 >>
        5: << 1 2 3 4 <5>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            self._process_test_list(5, ['<1> 2 3 4 5 >>', '<< 1 <2> 3 4 5 >>', '<< 1 2 <3> 4 5 >>', '<< 1 2 3 <4> 5 >>',
                                    '<< 1 2 3 4 <5>'])

        """
        ------ Всего страниц: 10, показывать соседей: 1 ------
        1:  <1> 2 >> 10
        2:  << 1 <2> 3 >> 10
        3:  1 << 2 <3> 4 >> 10
        4:  1 << 3 <4> 5 >> 10
        5:  1 << 4 <5> 6 >> 10
        6:  1 << 5 <6> 7 >> 10
        7:  1 << 6 <7> 8 >> 10
        8:  1 << 7 <8> 9 >> 10
        9:  1 << 8 <9> 10 >>
        10: 1 << 9 <10>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=1):
            self._process_test_list(10, ['<1> 2 >> 10', '<< 1 <2> 3 >> 10', '1 << 2 <3> 4 >> 10', '1 << 3 <4> 5 >> 10',
                                         '1 << 4 <5> 6 >> 10', '1 << 5 <6> 7 >> 10', '1 << 6 <7> 8 >> 10',
                                         '1 << 7 <8> 9 >> 10', '1 << 8 <9> 10 >>', '1 << 9 <10>'])

        """
        --- Всего страниц: 10, показывать соседей: 2 ---
        1:  <1> 2 3 >> 10
        2:  << 1 <2> 3 4 >> 10
        3:  << 1 2 <3> 4 5 >> 10
        4:  1 << 2 3 <4> 5 6 >> 10
        5:  1 << 3 4 <5> 6 7 >> 10
        6:  1 << 4 5 <6> 7 8 >> 10
        7:  1 << 5 6 <7> 8 9 >> 10
        8:  1 << 6 7 <8> 9 10 >>
        9:  1 << 7 8 <9> 10 >>
        10: 1 << 8 9 <10>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=2):
            self._process_test_list(10, ['<1> 2 3 >> 10', '<< 1 <2> 3 4 >> 10', '<< 1 2 <3> 4 5 >> 10',
                                         '1 << 2 3 <4> 5 6 >> 10', '1 << 3 4 <5> 6 7 >> 10', '1 << 4 5 <6> 7 8 >> 10',
                                         '1 << 5 6 <7> 8 9 >> 10', '1 << 6 7 <8> 9 10 >>', '1 << 7 8 <9> 10 >>',
                                         '1 << 8 9 <10>'])

        """
        --- Всего страниц: 10, показывать соседей: 20 ---
        1:  <1> 2 3 4 5 6 7 8 9 10 >>
        2:  << 1 <2> 3 4 5 6 7 8 9 10 >>
        3:  << 1 2 <3> 4 5 6 7 8 9 10 >>
        4:  << 1 2 3 <4> 5 6 7 8 9 10 >>
        5:  << 1 2 3 4 <5> 6 7 8 9 10 >>
        6:  << 1 2 3 4 5 <6> 7 8 9 10 >>
        7:  << 1 2 3 4 5 6 <7> 8 9 10 >>
        8:  << 1 2 3 4 5 6 7 <8> 9 10 >>
        9:  << 1 2 3 4 5 6 7 8 <9> 10 >>
        10: << 1 2 3 4 5 6 7 8 9 <10>
        """
        with self.settings(EFSW_COMM_PAGIN_NEIGHBOURS_COUNT=20):
            self._process_test_list(10, ['<1> 2 3 4 5 6 7 8 9 10 >>', '<< 1 <2> 3 4 5 6 7 8 9 10 >>',
                                         '<< 1 2 <3> 4 5 6 7 8 9 10 >>', '<< 1 2 3 <4> 5 6 7 8 9 10 >>',
                                         '<< 1 2 3 4 <5> 6 7 8 9 10 >>', '<< 1 2 3 4 5 <6> 7 8 9 10 >>',
                                         '<< 1 2 3 4 5 6 <7> 8 9 10 >>', '<< 1 2 3 4 5 6 7 <8> 9 10 >>',
                                         '<< 1 2 3 4 5 6 7 8 <9> 10 >>', '<< 1 2 3 4 5 6 7 8 9 <10>'])
            # И ещё раз - с query_string
            self._process_test_list(10, ['<1> 2 3 4 5 6 7 8 9 10 >>', '<< 1 <2> 3 4 5 6 7 8 9 10 >>',
                                         '<< 1 2 <3> 4 5 6 7 8 9 10 >>', '<< 1 2 3 <4> 5 6 7 8 9 10 >>',
                                         '<< 1 2 3 4 <5> 6 7 8 9 10 >>', '<< 1 2 3 4 5 <6> 7 8 9 10 >>',
                                         '<< 1 2 3 4 5 6 <7> 8 9 10 >>', '<< 1 2 3 4 5 6 7 <8> 9 10 >>',
                                         '<< 1 2 3 4 5 6 7 8 <9> 10 >>', '<< 1 2 3 4 5 6 7 8 9 <10>'], 'param=2')
