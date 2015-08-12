import re

# За идею регулярного выражения спасибо сюда:
# http://stackoverflow.com/questions/441739/regex-for-url-validation-with-parts-capturing
url_re = re.compile(
    "^(?P<scheme>\w+)://(?:(?P<username>.*?)(?::(?P<password>.*?)|)@)?(?P<host>[^:/@\s]+)(?:/|$)(?P<path>.*)$"
)


def format_url(url: str):
    url = url.replace('\\', '/')
    m = url_re.match(url)
    if m is None:
        raise WrongUrlFormatException(url)
    match_dict = m.groupdict()
    if _required_part_is_missing(match_dict):
        raise WrongUrlFormatException(url)
    return UrlFormatResult(**match_dict)


def is_url(url: str):
    return url_re.match(url.replace('\\', '/')) is not None


def _required_part_is_missing(match_dict):
    try:
        return not match_dict['scheme'] or not match_dict['host']
    except KeyError:
        return True


class WrongUrlFormatException(ValueError):
    msg = 'Неверный формат URL. Ожидалось "scheme://[username[:password]@]host/path/to/resource/", представлено "{0}".'

    def __init__(self, url):
        super().__init__(self.msg.format(url))


class UrlFormatResult:

    def __init__(self, scheme, username, password, host, path):
        self.scheme = scheme
        self.username = username
        self.password = password
        self.host = host
        self.path = path

    def scheme_is_win_share(self):
        return self.scheme in ['smb', 'cifs']

    def format_win(self):
        if self.scheme_is_win_share():
            return "\\\\{0}\{1}".format(self.host, self.path.replace('/', '\\'))
        else:
            return self.format()

    def _prepare_up(self):
        if self.username and self.password:
            up = "{0}:{1}@".format(self.username, self.password)
        elif self.username:
            up = "{0}@".format(self.username)
        else:
            up = ''
        return up

    def format(self):
        return "{0}://{1}{2}/{3}".format(
            self.scheme,
            self._prepare_up(),
            self.host,
            self.path
        )

    def __str__(self):
        return self.format()
