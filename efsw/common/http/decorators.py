from functools import wraps

from django.utils.decorators import available_attrs
from django.http import HttpResponseForbidden
from django.utils.safestring import mark_safe
from django.conf import settings

REQUIRE_AJAX_FORBIDDEN_TEMPLATE = """\
<html>
<head lang="en">
    <meta charset="UTF-8">
    <title>403 FORBIDDEN: AJAX requests only</title>
</head>
<body>
    <h1>403 FORBIDDEN</h1>
    <p>AJAX requests only.</p>
</body>
</html>
"""


def require_ajax(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view_func(request, *args, **kwargs):
        if not settings.EFSW_IGNORE_REQUIRE_AJAX and not request.is_ajax():
            return HttpResponseForbidden(mark_safe(REQUIRE_AJAX_FORBIDDEN_TEMPLATE))
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func
