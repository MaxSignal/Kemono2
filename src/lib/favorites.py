from src.database import get_cursor
from src.internals.cache.redis import (
    deserialize_dict_list,
    get_conn,
    serialize_dict_list
)
from src.lib.artist import get_artist, get_artist_last_updated
from src.lib.post import get_post
from src.utils.utils import get_value


def get_favorite_artists(account_id, reload=False):
    redis = get_conn()
    key = 'favorite_artists:' + str(account_id)
    favorites = redis.get(key)
    if favorites is None or reload:
        cursor = get_cursor()
        query = "select id, service, artist_id from account_artist_favorite where account_id = %s"
        cursor.execute(query, (account_id,))
        favorites = cursor.fetchall()
        redis.set(key, serialize_dict_list(favorites))
    else:
        favorites = deserialize_dict_list(favorites)

    artists = []
    for favorite in favorites:
        artist = get_artist(favorite['service'], favorite['artist_id'])
        last_updated = get_artist_last_updated(favorite['service'], favorite['artist_id'])
        if artist is not None:
            artist['faved_seq'] = favorite['id']
            artist['updated'] = last_updated
            artists.append(artist)
    return artists


def get_favorite_posts(account_id, reload=False):
    redis = get_conn()
    key = 'favorite_posts:' + str(account_id)
    favorites = redis.get(key)
    if favorites is None or reload:
        cursor = get_cursor()
        query = "select id, service, artist_id, post_id from account_post_favorite where account_id = %s"
        cursor.execute(query, (account_id,))
        favorites = cursor.fetchall()
        redis.set(key, serialize_dict_list(favorites))
    else:
        favorites = deserialize_dict_list(favorites)

    posts = []
    for favorite in favorites:
        post = get_post(favorite['post_id'], favorite['artist_id'], favorite['service'])
        if post is not None:
            post['faved_seq'] = favorite['id']
            posts.append(post)
    return posts


def is_artist_favorited(account_id, service, artist_id, reload=False):
    redis = get_conn()
    key = 'artist_favorited:' + str(account_id) + ':' + str(service) + str(artist_id)
    value = redis.get(key)
    if value is None or reload:
        cursor = get_cursor()
        query = "select 1 from account_artist_favorite where account_id = %s and service = %s and artist_id = %s"
        cursor.execute(query, (account_id, service, artist_id))
        value = cursor.fetchone() is not None
        redis.set(key, str(value))
    else:
        value = value.decode('utf-8') == 'True'

    return value


def is_post_favorited(account_id, service, artist_id, post_id, reload=False):
    redis = get_conn()
    key = 'post_favorited:' + str(account_id) + ':' + str(service) + str(artist_id) + ':' + str(post_id)
    value = redis.get(key)
    if value is None or reload:
        cursor = get_cursor()
        query = "select 1 from account_post_favorite where account_id = %s and service = %s and artist_id = %s and post_id = %s"
        cursor.execute(query, (account_id, service, artist_id, post_id))
        value = cursor.fetchone() is not None
        redis.set(key, str(value))
    else:
        value = value.decode('utf-8') == 'True'

    return value


def add_favorite_artist(account_id, service, artist_id):
    cursor = get_cursor()
    query = 'insert into account_artist_favorite (account_id, service, artist_id) values (%s, %s, %s) ON CONFLICT (account_id, service, artist_id) DO NOTHING'
    cursor.execute(query, (account_id, service, artist_id))
    get_favorite_artists(account_id, True)
    is_artist_favorited(account_id, service, artist_id, True)


def add_favorite_post(account_id, service, artist_id, post_id):
    cursor = get_cursor()
    query = 'insert into account_post_favorite (account_id, service, artist_id, post_id) values (%s, %s, %s, %s) ON CONFLICT (account_id, service, artist_id, post_id) DO NOTHING'
    cursor.execute(query, (account_id, service, artist_id, post_id))
    get_favorite_posts(account_id, True)
    is_post_favorited(account_id, service, artist_id, post_id, True)


def remove_favorite_artist(account_id, service, artist_id):
    cursor = get_cursor()
    query = 'delete from account_artist_favorite where account_id = %s and service = %s and artist_id = %s'
    cursor.execute(query, (account_id, service, artist_id))
    get_favorite_artists(account_id, True)
    is_artist_favorited(account_id, service, artist_id, True)


def remove_favorite_post(account_id, service, artist_id, post_id):
    cursor = get_cursor()
    query = 'delete from account_post_favorite where account_id = %s and service = %s and artist_id = %s and post_id = %s'
    cursor.execute(query, (account_id, service, artist_id, post_id))
    get_favorite_posts(account_id, True)
    is_post_favorited(account_id, service, artist_id, post_id, True)
