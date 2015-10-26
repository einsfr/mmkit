from django.conf import settings

from efsw.search.exceptions import WrongParametersException, EmptyQueryException, ExecutedQueryChangeException


class EsSearchQuery:

    BOOL_MUST = 1
    BOOL_SHOULD = 2
    BOOL_MUST_NOT = 3

    ORDER_ASC = 1
    ORDER_DESC = 2

    DEFAULT_FROM = 0
    DEFAULT_SIZE = 10

    MULTI_MATCH_QUERY_TYPE_BEST_FIELDS = 1
    MULTI_MATCH_QUERY_TYPE_MOST_FIELDS = 2
    MULTI_MATCH_QUERY_TYPE_CROSS_FIELDS = 3
    MULTI_MATCH_QUERY_TYPE_PHRASE = 4
    MULTI_MATCH_QUERY_TYPE_PHRASE_PREFIX = 5

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
        self._total_hits_count = None
        self._executed = 0
        self._hits_count = None

    def __str__(self):
        try:
            r = str(self.get_query_body())
        except EmptyQueryException:
            r = ''
        return r

    def __iter__(self):
        return self

    def __next__(self):
        if self._hits_iter_position < len(self):
            result = self.get_hits_list()[self._hits_iter_position]
            self._hits_iter_position += 1
            return result
        else:
            raise StopIteration

    def __len__(self):
        if self._hits_count is None:
            self._hits_count = len(self.get_hits_list())
        return self._hits_count

    @staticmethod
    def _convert_slice_to_from_size(k):
        if isinstance(k, slice):
            if k.start is not None:
                from_ = int(k.start)
            else:
                from_ = 0
            max_size = settings.EFSW_ELASTIC_MAX_SEARCH_RESULTS
            if k.stop is not None:
                size = int(k.stop) - from_
                if size > max_size:
                    raise ValueError('Количетсво результатов поиска не может быть больше {0}'.format(max_size))
            else:
                size = max_size
            if k.step is not None:
                step = int(k.step)
            else:
                step = None
            return from_, size, step
        elif isinstance(k, int):
            from_ = k
            size = 1
            step = None
            return from_, size, step
        else:
            raise TypeError

    def __getitem__(self, k):
        if not isinstance(k, (slice, int)):
            raise TypeError

        (from_, size, step) = self._convert_slice_to_from_size(k)
        if self._executed:
            # Если срез применяется к уже выполненному запросу - создаём копию с теми же параметрами и выполняем запрос
            # снова, но уже с другим срезом
            if from_ == self._from and size == self._size:
                # если только этот срез не такой же, как предыдущий
                if step is not None:
                    return self.get_hits_list()[::step]
                else:
                    return self.get_hits_list()
            else:
                return self.copy()[k]

        sliced_obj = self.copy()
        result = sliced_obj.from_size(from_, size).get_hits_list()
        if step is not None:
            return result[::step]
        else:
            return result

    def copy(self):
        c = self.__class__(self._es_cm, self._index_name, self._doc_type, self._bool_default)
        c._queries = self._queries
        c._sort = self._sort
        c._filters = self._filters
        c._size = self._size
        c._from = self._from
        return c

    def query_match_all(self):
        if self._executed:
            raise ExecutedQueryChangeException()
        self._queries.append(
            (
                {
                    'match_all': {}
                },
            )
        )
        return self

    def query_multi_match(self, query, fields, bool_type=None, query_type=None):
        if self._executed:
            raise ExecutedQueryChangeException()
        bool_type = bool_type if bool_type is not None else self._bool_default
        query_body = {
            'query': query,
            'fields': fields,
        }
        if query_type is not None:
            if query_type == self.MULTI_MATCH_QUERY_TYPE_BEST_FIELDS:
                query_body['type'] = 'best_fields'
            elif query_type == self.MULTI_MATCH_QUERY_TYPE_MOST_FIELDS:
                query_body['type'] = 'most_fields'
            elif query_type == self.MULTI_MATCH_QUERY_TYPE_CROSS_FIELDS:
                query_body['type'] = 'cross_fields'
            elif query_type == self.MULTI_MATCH_QUERY_TYPE_PHRASE:
                query_body['type'] = 'phrase'
            elif query_type == self.MULTI_MATCH_QUERY_TYPE_PHRASE_PREFIX:
                query_body['type'] = 'phrase_prefix'
        self._queries.append(
            (
                {
                    'multi_match': query_body
                },
                bool_type
            )
        )
        return self

    def sort_field(self, field, order=ORDER_ASC):
        if self._executed:
            raise ExecutedQueryChangeException()
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
        if self._executed:
            raise ExecutedQueryChangeException()
        bool_type = bool_type if bool_type is not None else self._bool_default
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
        if self._executed:
            raise ExecutedQueryChangeException()
        bool_type = bool_type if bool_type is not None else self._bool_default
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
        if self._executed:
            raise ExecutedQueryChangeException()
        self._from = from_param
        self._size = size_param
        return self

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

    def get_total_hits_count(self):
        # TODO: по-хорошему, если запрос ещё не выполнялся, то его можно выполнить как count, а не как search
        if self._total_hits_count is None:
            self._total_hits_count = int(self.get_result()['hits']['total'])
        return self._total_hits_count

    def executed(self):
        return bool(self._executed)

    def get_hits_list(self):
        return self.get_result()['hits']['hits']