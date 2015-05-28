from django.http import JsonResponse


class JsonWithStatusResponse(JsonResponse):

    STATUS_OK = 'ok'
    STATUS_ERROR = 'err'

    def __init__(self, data='', json_status=STATUS_OK, status_ext=None, **kwargs):
        super().__init__(
            {
                'status': json_status,
                'status_ext': status_ext if status_ext is not None else '',
                'data': data,
            },
            **kwargs
        )

    @classmethod
    def ok(cls, data='', status_ext=None, **kwargs):
        return cls(data, cls.STATUS_OK, status_ext, **kwargs)

    @classmethod
    def error(cls, data='', status_ext=None, **kwargs):
        return cls(data, cls.STATUS_ERROR, status_ext, **kwargs)