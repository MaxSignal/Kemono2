from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit
from datetime import datetime
from flask import request, g
import json
import random
import hashlib
from configs.derived_vars import is_development

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
    "boosty",
    "afdian"
]

# because fanbox requires `post_id` and `artist_id` for post link
# any generic call to `paysite.post.link()` should have 2 arguments
paysites = {
    "patreon": {
        "title": "Patreon",
        "user": {
            "profile": lambda user_id: f"https://www.patreon.com/user?u={user_id}",
        },
        "post": {
            "link": lambda post_id: f"https://www.patreon.com/posts/{post_id}",
        },
    },
    "fanbox": {
        "title": "Pixiv Fanbox",
        "user": {
            "profile": lambda user_id: f"https://www.pixiv.net/fanbox/creator/{user_id}",
        },
        "post": {
            "link": lambda post_id, user_id: f"https://www.pixiv.net/fanbox/creator/{user_id}/post/{post_id}",
        },
    },
    "gumroad": {
        "title": "Gumroad",
        "user": {
            "profile": lambda user_id: f"https://gumroad.com/{user_id}",
        },
        "post": {
            "link": lambda post_id: f"https://gumroad.com/l/{post_id}",
        },
    },
    "subscribestar": {
        "title": "SubscribeStar",
        "user": {
            "profile": lambda user_id: f"https://subscribestar.adult/{user_id}",
        },
        "post": {
            "link": lambda post_id: f"https://subscribestar.adult/posts/{post_id}",
        },
    },
    "dlsite": {
        "title": "DLsite",
        "user": {
            "profile": lambda user_id: f"https://www.dlsite.com/eng/circle/profile/=/maker_id/{user_id}",
        },
        "post": {
            "link": lambda post_id: f"https://www.dlsite.com/ecchi-eng/work/=/product_id/{post_id}",
        },
    },
    "discord": {
        "title": "Discord",
        "user": {
            "profile": lambda user_id: f"",
        },
        "post": {
            "link": lambda post_id: f"",
        },
    },
    "fantia": {
        "title": "Fantia",
        "user": {
            "profile": lambda user_id: f"https://fantia.jp/fanclubs/{user_id}",
        },
        "post": {
            "link": lambda post_id: f"https://fantia.jp/posts/{post_id}",
        },
    },
    "boosty": {
        "title": "Boosty",
        "user": {
            "profile": lambda user_id: f"",
        },
        "post": {
            "link": lambda post_id: f"",
        },
    },
    "afdian": {
        "title": "Afdian",
        "user": {
            "profile": lambda user_id: f"",
        },
        "post": {
            "link": lambda post_id: f"",
        },
    }
}

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

def get_value(d, key, default = None):
    if key in d:
        return d[key]
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

def take(num, l):
    if len(l) <= num:
        return l
    return l[:num]

def offset(num, l):
    if len(l) <= num:
        return []
    return l[num:]

def limit_int(i: int, limit: int):
    if i > limit:
        return limit
    return i

def parse_int(string, default = 0):
    try:
        return int(string)
    except Exception:
        return default

def render_page_data():
    return json.dumps(g.page_data)

def get_import_id(data):
    salt = str(random.randrange(0, 1000))
    return take(16, hashlib.sha256((data + salt).encode('utf-8')).hexdigest())

# doing it in the end to avoid circular import error
if is_development:
    from src.dev_only.internals import service_name, kemono_dev
    paysite_list.append(service_name)
    paysites[service_name] = kemono_dev
