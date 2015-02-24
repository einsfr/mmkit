from efsw.common.search.exceptions import WrongParametersException,\
    EmptyQueryException


class EsSearchQuery():

    BOOL_MUST = 1
    BOOL_SHOULD = 2
    BOOL_MUST_NOT = 3

    ORDER_ASC = 1
    ORDER_DESC = 2

    DEFAULT_FROM = 0
    DEFAULT_SIZE = 10

    def __init__(self, es_cm, index_name=None, doc_type=None, bool_default=None):
        self._es_cm = es_cm
        self._index_name = index_name
        self._doc_type = doc_type
        if bool_default is None:
            self._bool_default = self.BOOL_MUST
        elif bool_default in [self.BOOL_MUST, self.BOOL_SHOULD, self.BOOL_MUST_NOT]:
            self._bool_default = bool_default
        else:
            msg = 'Параметр bool_default должен иметь значение из следующих: BOOL_MUST, BOOL_SHOULD, BOOL_MUST_NOT'
            raise WrongParametersException(msg)
        self._queries = []
        self._sort = []
        self._filters = []
        self._size = None
        self._from = None
        self._query_body = None
        self._result = None
        self._hits_iter_position = 0
        self._hits_count = 0
        self._executed = 0

    def __str__(self):
        try:
            r = self.get_query_body()
        except EmptyQueryException:
            r = ''
        return r

    def __iter__(self):
        return self

    def __next__(self):
        if self._hits_iter_position < self.get_hits_count():
            result = self.get_result()['hits']['hits'][self._hits_iter_position]
            self._hits_iter_position += 1
            return result
        else:
            raise StopIteration

    def __len__(self):
        return self.get_hits_count()

    def query_match_all(self):
        self._queries.append(
            (
                {
                    'match_all': {}
                },
            )
        )
        return self

    def query_multi_match(self, query, fields, bool_type=None):
        if not bool_type:
            bool_type = self._bool_default
        self._queries.append(
            (
                {
                    'multi_match': {
                        'query': query,
                        'fields': fields,
                    }
                },
                bool_type
            )
        )
        return self

    def sort_field(self, field, order=ORDER_ASC):
        if order == self.ORDER_ASC:
            order_str = 'asc'
        else:
            order_str = 'desc'
        self._sort.append(
            (
                {
                    field: {
                        'order': order_str
                    }
                },
            )
        )
        return self

    def filter_terms(self, field, values_list, bool_type=None):
        if not bool_type:
            bool_type = self._bool_default
        self._filters.append(
            (
                {
                    'terms': {
                        field: values_list
                    }
                },
                bool_type
            )
        )
        return self

    def filter_range(self, field, bool_type=None, **kwargs):
        if not bool_type:
            bool_type = self._bool_default
        if kwargs.get('gte') and kwargs.get('gt'):
            msg = 'Одно поле в фильтре range не может одновремнено иметь ограничения >= и >'
            raise WrongParametersException(msg)
        if kwargs.get('lte') and kwargs.get('lt'):
            msg = 'Одно поле в фильтре range не может одновремнено иметь ограничения <= и <'
            raise WrongParametersException(msg)
        range_dict = dict((k, v) for k, v in kwargs.items() if k in ['gte', 'gt', 'lte', 'lt'])
        self._filters.append(
            (
                {
                    'range': {
                        field: range_dict
                    }
                },
                bool_type
            )
        )
        return self

    def from_size(self, from_param=DEFAULT_FROM, size_param=DEFAULT_SIZE):
        self._from = from_param
        self._size = size_param

    def get_query_body(self):
        if self._query_body is not None:
            return self._query_body

        # ЗАПРОСЫ

        if len(self._queries) > 1:
            # Если запросов много - нужно объединять их через bool
            must_queries = [x[0] for x in self._queries if x[1] == self.BOOL_MUST]
            should_queries = [x[0] for x in self._queries if x[1] == self.BOOL_SHOULD]
            must_not_queries = [x[0] for x in self._queries if x[1] == self.BOOL_MUST_NOT]
            queries = {
                'bool': {}
            }
            if must_queries:
                queries['bool']['must'] = must_queries
            if should_queries:
                queries['bool']['should'] = should_queries
            if must_not_queries:
                queries['bool']['must_not'] = must_not_queries
            query = {
                'query': queries
            }
        elif len(self._queries) == 1:
            # Если запрос всего один
            query = {
                'query': self._queries[0][0]
            }
        else:
            query = {}

        # ФИЛЬТРЫ

        if not len(self._filters):
            # Если фильтров нет - запрос остаётся просто запросом
            if not query:
                # Если фильтров нет и запросов нет - нечего и искать
                msg = 'Списки запросов и фильтров пусты'
                raise EmptyQueryException(msg)
        else:
            # А если они есть - он становится фильтрованным запросом
            query = {
                'query': {
                    'filtered': query
                }
            }
            if len(self._filters) > 1:
                # Если фильтров много - нужно объединять их через bool
                must_filters = [x[0] for x in self._filters if x[1] == self.BOOL_MUST]
                should_filters = [x[0] for x in self._filters if x[1] == self.BOOL_SHOULD]
                must_not_filters = [x[0] for x in self._filters if x[1] == self.BOOL_MUST_NOT]
                filters = {
                    'bool': {}
                }
                if must_filters:
                    filters['bool']['must'] = must_filters
                if should_filters:
                    filters['bool']['should'] = should_filters
                if must_not_filters:
                    filters['bool']['must_not'] = must_not_filters
                query['query']['filtered']['filter'] = filters
            else:
                # Если фильтр всего один - объединять ничего не нужно
                query['query']['filtered']['filter'] = self._filters[0][0]

        # СОРТИРОВКА

        if len(self._sort):
            query['sort'] = [x[0] for x in self._sort]
            query['sort'].append('_score')

        # ОГРАНИЧЕНИЕ НА РАЗМЕР ВЫБОРКИ (FROM/SIZE)

        if self._from:
            query['from'] = self._from
        if self._size:
            query['size'] = self._size

        # СОХРАНЕНИЕ СОБРАННОГО ТЕЛА ЗАПРОСА

        self._query_body = query
        return self._query_body

    def _execute_query(self):
        self._executed += 1  # Для нужд тестирования, чтобы удостовериться, что ни один запрос не выполняется дважды
        return self._es_cm.get_es().search(
            index=self._es_cm.prefix_index_name(self._index_name),
            doc_type=self._doc_type,
            body=self.get_query_body()
        )

    def get_result(self):
        if self._result is None:
            self._result = self._execute_query()
        return self._result

    def get_hits_count(self):
        # TODO: по-хорошему, если запрос ещё не выполнялся, то его можно выполнить как count, а не как search
        if not self._hits_count:
            self._hits_count = int(self.get_result()['hits']['total'])
        return self._hits_count

    def executed(self):
        return bool(self._executed)