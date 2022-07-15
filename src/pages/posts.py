from flask import Blueprint, render_template, make_response, redirect, url_for, request
from src.lib.post import get_render_data_for_posts
from src.lib.posts import get_all_posts, get_all_posts_for_query, count_all_posts, count_all_posts_for_query
from src.utils.utils import limit_int, parse_int
from datetime import datetime


posts = Blueprint('posts', __name__)


@posts.route('/posts')
def get_posts():
    props = {
        'currentPage': 'posts'
    }
    base = request.args.to_dict()
    base.pop('o', None)

    query = request.args.get('q', default='').strip()
    offset = parse_int(request.args.get('o'), 0)
    props['limit'] = 25

    if not query or len(query) < 2:
        results = get_all_posts(offset)
        props['count'] = count_all_posts()
    else:
        results = get_all_posts_for_query(query, offset)
        props['count'] = count_all_posts_for_query(query)

    (result_previews, result_attachments, result_flagged,
     result_after_kitsune, result_is_image) = get_render_data_for_posts(results)

    response = make_response(render_template(
        'posts.html',
        props=props,
        results=results,
        base=base,
        result_previews=result_previews,
        result_attachments=result_attachments,
        result_flagged=result_flagged,
        result_after_kitsune=result_after_kitsune,
        result_is_image=result_is_image
    ), 200)
    response.headers['Cache-Control'] = 'no-store, max-age=0'
    return response
