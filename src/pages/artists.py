from flask import (Blueprint, make_response, redirect, render_template,
                   request, session, url_for)

from configs.derived_vars import is_development
from src.lib.account import load_account
from src.lib.artist import (get_all_non_discord_artists, get_artist,
                            get_artist_post_count, get_artists_by_service,
                            get_artists_by_update_time,
                            get_count_of_artists_faved,
                            get_top_artists_by_faves)
from src.lib.dms import count_user_dms, get_artist_dms
from src.lib.favorites import is_artist_favorited
from src.lib.post import (get_all_posts_by_artist, get_artist_posts,
                          get_render_data_for_posts, is_post_flagged)
from src.utils.utils import (limit_int, offset, parse_int, sort_dict_list_by,
                             take)
from src.internals.database.database import get_cursor
from .artists_types import ArtistDMsProps, ArtistPageProps

artists = Blueprint('artists', __name__)


@artists.route('/artists')
def list():
    props = {
        'currentPage': 'artists'
    }
    base = request.args.to_dict()
    base.pop('o', None)

    # q = request.args.get('q')
    # commit = request.args.get('commit')
    # service = request.args.get('service')
    # sort_by = request.args.get('sort_by')
    # order = request.args.get('order')
    offset = parse_int(request.args.get('o'), 0)
    limit = 25

    (results, total_count) = ([], 0)
    results = get_top_artists_by_faves(offset, limit)
    total_count = get_count_of_artists_faved()
    props['display'] = 'most popular artists'

    props['count'] = total_count
    props['limit'] = limit
    response = make_response(render_template(
        'artists.html',
        props=props,
        results=results,
        base=base
    ), 200)
    response.headers['Cache-Control'] = 's-maxage=60'
    return response


@artists.route('/artists/updated')
def updated():
    props = {
        'currentPage': 'artists'
    }
    base = request.args.to_dict()
    base.pop('o', None)

    offset = parse_int(request.args.get('o'), 0)
    limit = 25

    props['limit'] = limit

    results = get_artists_by_update_time(offset=offset)
    props["count"] = len(get_all_non_discord_artists())

    base = request.args.to_dict()
    base.pop('o', None)

    response = make_response(render_template(
        'updated.html',
        base=base,
        props=props,
        results=results
    ), 200)
    response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
    return response


@artists.route('/<service>/user/<artist_id>')
def get(service: str, artist_id: str):
    # cursor = get_cursor()

    base = request.args.to_dict()
    base.pop('o', None)
    base["service"] = service
    base["artist_id"] = artist_id

    offset = parse_int(request.args.get('o'), 0)
    query = request.args.get('q', default='').strip()
    limit = limit_int(int(request.args.get('limit') or 25), 50)

    favorited = False
    account = load_account()
    if account is not None:
        favorited = is_artist_favorited(account['id'], service, artist_id)

    (posts, total_count) = ([], 0)
    if not query or len(query) < 3:
        (posts, total_count) = get_artist_post_page(artist_id, service, offset, limit)
    else:
        (posts, total_count) = do_artist_post_search(artist_id, service, query, offset, limit)

    artist = get_artist(service, artist_id)
    if artist is None:
        return redirect(url_for('artists.list'))
    display_data = make_artist_display_data(artist)
    dm_count = count_user_dms(service, artist_id)

    (result_previews, result_attachments, result_flagged,
     result_after_kitsune, result_is_image) = get_render_data_for_posts(posts)

    props = ArtistPageProps(
        id=artist_id,
        service=service,
        session=session,
        name=artist['name'],
        count=total_count,
        limit=limit,
        favorited=favorited,
        artist=artist,
        display_data=display_data,
        dm_count=dm_count
    )

    response = make_response(render_template(
        'user.html',
        props=props,
        base=base,
        results=posts,
        result_previews=result_previews,
        result_attachments=result_attachments,
        result_flagged=result_flagged,
        result_after_kitsune=result_after_kitsune,
        result_is_image=result_is_image
    ), 200)
    response.headers['Cache-Control'] = 's-maxage=60'
    return response


@artists.route('/<service>/user/<artist_id>/dms')
def get_dms(service: str, artist_id: str):
    # pagination might be added at some point if we need it, but considering how few dms most artists end up having, we probably won't
    # base = request.args.to_dict()
    # base.pop('o', None)
    # base["service"] = service
    # base["artist_id"] = artist_id

    # offset = int(request.args.get('o') or 0)
    # query = request.args.get('q')
    # limit = limit_int(int(request.args.get('limit') or 25), 50)

    artist = get_artist(service, artist_id)
    if artist is None:
        return redirect(url_for('artists.list'))

    dms = get_artist_dms(service, artist_id)
    # @REVIEW: TypeError: __init__() got an unexpected keyword argument 'id'
    # @RESPONSE: fixed
    props = ArtistDMsProps(
        id=artist_id,
        service=service,
        session=session,
        artist=artist,
        display_data=make_artist_display_data(artist),
        dms=dms,
    )

    response = make_response(render_template(
        'artist/dms.html',
        props=props,
    ), 200)
    response.headers['Cache-Control'] = 's-maxage=60'
    return response


def get_artist_search_results(q, service, sort_by, order, o, limit):
    if service:
        artists = get_artists_by_service(service)
    else:
        artists = get_all_non_discord_artists()

    # page = []
    matches = []
    q_lower = q.lower()
    for artist in artists:
        if q_lower in artist['name'].lower():
            matches.append(artist)

    matches = sort_dict_list_by(matches, sort_by, order == 'desc')

    return (take(limit, offset(o, matches)), len(matches))


def do_artist_post_search(id, service, search, o, limit):
    posts = get_all_posts_by_artist(id, service)
    search = search.lower()

    matches = []
    for post in posts:
        if search in post['content'].lower() or search in post['title'].lower():
            matches.append(post)

    matches = sort_dict_list_by(matches, 'published', True)

    return (take(limit, offset(o, matches)), len(matches))


def get_artist_post_page(artist_id, service, offset, limit):
    posts = get_artist_posts(artist_id, service, offset, limit, 'published desc')
    total_count = get_artist_post_count(service, artist_id)
    return (posts, total_count)


def make_artist_display_data(artist: dict):
    artist_id = str(artist['id'])
    service_name = artist['service']
    data_by_service_name = {
        'patreon': {
            'service': 'Patreon',
            'href': f"https://www.patreon.com/user?u={artist_id}",
        },
        'fanbox': {
            'service': 'Fanbox',
            'href': f"https://www.pixiv.net/fanbox/creator/{artist_id}",
        },
        'gumroad': {
            'service': 'Gumroad',
            'href': f"https://gumroad.com/{artist_id}",
        },
        'subscribestar': {
            'service': 'SubscribeStar',
            'href': f"https://subscribestar.adult/{artist_id}",
        },
        'dlsite': {
            'service': 'DLsite',
            'href': f"https://www.dlsite.com/eng/circle/profile/=/maker_id/{artist_id}",
        },
        'fantia': {
            'service': 'Fantia',
            'href': f"https://fantia.jp/fanclubs/{artist_id}",
        },
    }

    if is_development:
        from development import kemono_dev
        data_by_service_name[kemono_dev.name] = dict(
            service=kemono_dev.title,
            href=kemono_dev.user.profile
        )
    data = data_by_service_name[service_name]
    data['proxy'] = f"/{service_name}/user/{artist_id}"

    return data
