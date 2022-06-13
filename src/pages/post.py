import datetime
import re
from pathlib import PurePath

from bleach.sanitizer import Cleaner
from flask import (
    Blueprint,
    make_response,
    redirect,
    render_template,
    request,
    url_for
)

from src.internals.cache.flask_cache import cache
from src.lib.account import load_account
from src.lib.artist import get_artist
from src.lib.favorites import is_post_favorited
from src.lib.post import (
    get_next_post_id,
    get_post,
    get_post_comments,
    get_previous_post_id,
    is_post_flagged
)
from src.utils.utils import make_cache_key

post = Blueprint('post', __name__)


@post.route('/<service>/user/<user_id>/post/<post_id>/prev')
def post_prev(service, user_id, post_id):
    previous_post_id = get_previous_post_id(post_id, user_id, service)

    previous_post = None
    if previous_post_id is not None:
        previous_post = get_post(previous_post_id, user_id, service)

    if not previous_post:
        return redirect(request.headers.get('Referer') if request.headers.get('Referer') else '/')
    else:
        return redirect(url_for('post.get', service=previous_post['service'], artist_id=previous_post['user'], post_id=previous_post['id']))


@post.route('/<service>/user/<user_id>/post/<post_id>/next')
def post_next(service, user_id, post_id):
    next_post_id = get_next_post_id(post_id, user_id, service)

    next_post = None
    if next_post_id is not None:
        next_post = get_post(next_post_id, user_id, service)

    if not next_post:
        return redirect(request.headers.get('Referer') if request.headers.get('Referer') else '/')
    else:
        return redirect(url_for('post.get', service=next_post['service'], artist_id=next_post['user'], post_id=next_post['id']))


@post.route('/<service>/user/<artist_id>/post/<post_id>')
def get(service, artist_id, post_id):
    # cursor = get_cursor()
    props = {
        'currentPage': 'posts',
        'service': service if service else 'patreon'
    }

    post = get_post(post_id, artist_id, service)
    if post is None:
        response = redirect(url_for('artists.get', service=service, artist_id=artist_id))
        return response

    comments = get_post_comments(post_id, service)

    favorited = False
    account = load_account()
    if account is not None:
        favorited = is_post_favorited(account['id'], service, artist_id, post_id)

    artist = get_artist(service, artist_id)

    previews = []
    attachments = []
    if len(post['file']):
        if re.search("\.(gif|jpe?g|jpe|png|webp)$", post['file']['path'], re.IGNORECASE):  # noqa w605
            previews.append({
                'type': 'thumbnail',
                'name': post['file'].get('name'),
                'path': post['file']['path'].replace('https://kemono.party', '')
            })
        else:
            attachments.append({
                'path': post['file']['path'].replace('https://kemono.party', ''),
                'name': post['file'].get('name')
            })
    if len(post['embed']):
        previews.append({
            'type': 'embed',
            'url': post['embed']['url'],
            'subject': post['embed']['subject'],
            'description': post['embed']['description']
        })
    for attachment in post['attachments']:
        if re.search("\.(gif|jpe?g|jpe|png|webp)$", attachment['path'], re.IGNORECASE):  # noqa w605
            previews.append({
                'type': 'thumbnail',
                'name': attachment['name'],
                'path': attachment['path'].replace('https://kemono.party', '')
            })
        else:
            file_extension = PurePath(attachment['path']).suffix
            # filename without extension
            stem = PurePath(attachment['path']).stem
            attachments.append({
                'path': attachment['path'],
                'name': attachment.get('name'),
                'extension': file_extension,
                'stem': stem
            })
    scrub = Cleaner(
        tags=['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul',
              'img', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'span', 'ul', 'ol', 'li'],
        attributes={
            'a': ['href', 'title'],
            'abbr': ['title'],
            'acronym': ['title'],
            'img': ['src']
        },
        strip=True
    )
    post['content'] = scrub.clean(post['content'])

    props['artist'] = artist
    props['flagged'] = is_post_flagged(service, artist_id, post_id)
    props['favorited'] = favorited
    props['after_kitsune'] = post['added'] > datetime.datetime(2020, 12, 22, 0, 0, 0, 0)
    response = make_response(render_template(
        'post.html',
        props=props,
        post=post,
        comments=comments,
        result_previews=previews,
        result_attachments=attachments,
    ), 200)
    response.headers['Cache-Control'] = 's-maxage=60'
    return response
