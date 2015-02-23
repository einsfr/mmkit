import json

from efsw.common.search.exceptions import WrongFilterParametersException
from efsw.common.search.elastic import EsConnectionManager


class EsSearchQuery():

    BOOL_MUST = 1
    BOOL_SHOULD = 2
    BOOL_MUST_NOT = 3
    BOOL_DEFAULT = BOOL_MUST

    ORDER_ASC = 1
    ORDER_DESC = 2

    def __init__(self, es_cm: EsConnectionManager, index_name: str=None, doc_type: str=None):
        self._es_cm = es_cm
        self._index_name = index_name
        self._doc_type = doc_type
        self._queries = []
        self._sort = []
        self._filters = []
        self._size = None
        self._from = None
        self._query_body = None
        self._result = None

    def __iter__(self) -> list:
        return self.get_result()['hits']['hits']

    def query_match_all(self) -> EsSearchQuery:
        self._queries.append({
            'match_all': {}
        })
        return self

    def query_multi_match(self, query: str, fields: list, bool_type: int=BOOL_DEFAULT) -> EsSearchQuery:
        self._queries.append({
            'multi_match': {
                'query': query,
                'fields': fields,
            },
            'bool_type': bool_type
        })
        return self

    def sort_field(self, field: str, order: int=ORDER_ASC) -> EsSearchQuery:
        if order == self.ORDER_ASC:
            order_str = 'asc'
        else:
            order_str = 'desc'
        self._sort.append({
            field: {
                'order': order_str
            }
        })
        return self

    def filter_terms(self, field: str, values_list: list, bool_type: int=BOOL_DEFAULT) -> EsSearchQuery:
        self._filters.append({
            'terms': {
                field: values_list
            },
            'bool_type': bool_type
        })
        return self

    def filter_range(self, field: str, bool_type: int=BOOL_DEFAULT, **kwargs) -> EsSearchQuery:
        if kwargs.get('gte') and kwargs.get('gt'):
            msg = 'Одно поле в фильтре range не может одновремнено иметь ограничения >= и >'
            raise WrongFilterParametersException(msg)
        if kwargs.get('lte') and kwargs.get('lt'):
            msg = 'Одно поле в фильтре range не может одновремнено иметь ограничения <= и <'
            raise WrongFilterParametersException(msg)
        range_dict = dict((k, v) for k, v in kwargs if k in ['gte', 'gt', 'lte', 'lt'])
        self._filters.append({
            'range': {
                field: range_dict
            },
            'bool_type': bool_type
        })
        return self

    def _get_query_body(self) -> dict:
        if self._query_body is not None:
            return self._query_body
        # TODO: Здесь каким-то хитрым образом выстраивается тело запроса
        return self._query_body

    def _execute_query(self) -> dict:
        return self._es_cm.get_es().search(
            index=self._es_cm.prefix_index_name(self._index_name),
            doc_type=self._doc_type,
            body=json.dumps(self._get_query_body())
        )

    def get_result(self) -> dict:
        if self._result is None:
            self._result = self._execute_query()
        return self._result