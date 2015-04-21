from django.http import JsonResponse


class JsonWithStatusResponse(JsonResponse):

    STATUS_OK = 'ok'
    STATUS_ERROR = 'err'

    def __init__(self, data='', json_status=STATUS_OK, **kwargs):
        super().__init__(
            {
                'status': json_status,
                'data': data,
            },
            **kwargs
        )

    @classmethod
    def ok(cls, data, **kwargs):
        return cls(data, cls.STATUS_OK, **kwargs)

    @classmethod
    def error(cls, data, **kwargs):
        return cls(data, cls.STATUS_ERROR, **kwargs)