from flask import Blueprint, request, make_response, render_template

from ..utils.utils import make_cache_key
from ..internals.cache.flask_cache import cache

dmca = Blueprint('dmca', __name__)

@dmca.route('/dmca')
@cache.cached(key_prefix=make_cache_key)
def get_support():
    props = {}
    base = request.args.to_dict()
    base.pop('o', None)
    response = make_response(render_template(
        'dmca.html',
        props = props,
        base = base
    ), 200)
    response.headers['Cache-Control'] = 's-maxage=60'
    return response

@dmca.route('/exclusions')
@cache.cached(key_prefix=make_cache_key)
def get_exclusions():
    props = {}
    base = request.args.to_dict()
    base.pop('o', None)
    response = make_response(render_template(
        'content_policy.html',
        props = props,
        base = base
    ), 200)
    response.headers['Cache-Control'] = 's-maxage=60'
    return response
