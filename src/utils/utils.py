import hashlib
import json
import random
from base64 import b64encode
from dataclasses import fields
from datetime import datetime
from typing import Optional, TypedDict
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from flask import g, request

from configs.derived_vars import is_development
from src.types.paysites import Paysites


class TDOption(TypedDict):
    """
    `<option>` attributes plus `title` for macro.
    """
    value: str
    title: Optional[str]
    selected: Optional[str]


freesites = {
    "kemono": {
        "title": "Kemono",
        "user": {
            "profile": lambda service, user_id: f"/{service}/{ 'server' if service == 'discord' else 'user' }/{user_id}",
            "icon": lambda service, user_id: f"/icons/{service}/{user_id}",
            "banner": lambda service, user_id: f"/banners/{service}/{user_id}"
        },
        "post": {
            "link": lambda service, user_id, post_id: f"/{service}/user/{user_id}/post/{post_id}"
        }
    }
}

paysite_list = [
    "patreon",
    "fanbox",
    "gumroad",
    "subscribestar",
    "dlsite",
    "discord",
    "fantia",
]

paysites = Paysites()
# pre-configured `options`
# because Jinja cannot into list comprehensions
paysite_options = [
    TDOption(
        value=field.name,
        title=paysites[field.name].title
    )
    for field
    in fields(paysites)
]


def set_query_parameter(url, param_name, param_value):
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)

    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


def make_cache_key(*args, **kwargs):
    return request.full_path


def relative_time(date):
    """Take a datetime and return its "age" as a string.
    The age can be in second, minute, hour, day, month or year. Only the
    biggest unit is considered, e.g. if it's 2 days and 3 hours, "2 days" will
    be returned.
    Make sure date is not in the future, or else it won't work.
    Original Gist by 'zhangsen' @ https://gist.github.com/zhangsen/1199964
    """

    def formatn(n, s):
        """Add "s" if it's plural"""

        if n == 1:
            return "1 %s" % s
        elif n > 1:
            return "%d %ss" % (n, s)

    def qnr(a, b):
        """Return quotient and remaining"""

        return a / b, a % b

    class FormatDelta:

        def __init__(self, dt):
            now = datetime.now()
            delta = now - dt
            self.day = delta.days
            self.second = delta.seconds
            self.year, self.day = qnr(self.day, 365)
            self.month, self.day = qnr(self.day, 30)
            self.hour, self.second = qnr(self.second, 3600)
            self.minute, self.second = qnr(self.second, 60)

        def format(self):
            for period in ['year', 'month', 'day', 'hour', 'minute', 'second']:
                n = getattr(self, period)
                if n >= 1:
                    return '{0} ago'.format(formatn(n, period))
            return "just now"

    return FormatDelta(date).format()


def delta_key(e):
    return e['delta_date']


def allowed_file(mime, accepted):
    return any(x in mime for x in accepted)


def get_value(dictionary, key, default=None):
    if key in dictionary:
        return dictionary[key]
    return default


def url_is_for_non_logged_file_extension(path):
    parts = path.split('/')
    if len(parts) == 0:
        return False

    blocked_extensions = ['js', 'css', 'ico', 'svg']
    for extension in blocked_extensions:
        if ('.' + extension) in parts[-1]:
            return True
    return False


def sort_dict_list_by(list_var, key, reverse=False):
    return sorted(list_var, key=lambda v: (v[key] is None, v[key]), reverse=reverse)


def restrict_value(value, allowed, default=None):
    if value not in allowed:
        return default
    return value


def take(num, list_var):
    if len(list_var) <= num:
        return list_var
    return list_var[:num]


def offset(num, list_var):
    if len(list_var) <= num:
        return []
    return list_var[num:]


def limit_int(integer: int, limit: int):
    if integer > limit:
        return limit
    return integer


def parse_int(string: str, default: int = 0):
    try:
        return int(string)
    except Exception:
        return default


def render_page_data():
    return json.dumps(g.page_data)


def get_import_id(data):
    salt = str(random.randrange(0, 1000))
    return take(16, hashlib.sha256((data + salt).encode('utf-8')).hexdigest())


def encode_text_query(query: str):
    return b64encode(query.encode('utf-8')).decode('utf-8') if query else ""


# doing it in the end to avoid circular import error
if is_development:
    from development import kemono_dev
    paysite_list.append(kemono_dev.name)
    setattr(paysites, kemono_dev.name, kemono_dev)
