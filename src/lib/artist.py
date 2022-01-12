from ..internals.cache.redis import get_conn, KemonoRedisLock
from ..internals.database.database import get_cursor
from ..utils.utils import get_value
from ..types.kemono import User
from threading import Lock
import redis_lock
import ujson
import dateutil
import copy
import datetime
import time


def get_top_artists_by_faves(offset, count, reload=False):
    redis = get_conn()
    key = 'top_artists:' + str(offset) + ':' + str(count)
    artists = redis.get(key)
    if artists is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = """
                SELECT l.*, count(*)
                FROM lookup l
                INNER JOIN account_artist_favorite aaf
                    ON l.id = aaf.artist_id AND l.service = aaf.service
                WHERE aaf.service != 'discord-channel'
                GROUP BY (l.id, l.service)
                ORDER BY count(*) DESC
                OFFSET %s
                LIMIT %s
            """
            cursor.execute(query, (offset, count,))
            artists = cursor.fetchall()
            redis.set(key, serialize_artists(artists), ex=3600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_top_artists_by_faves(offset, count, reload=reload)
    else:
        artists = deserialize_artists(artists)
    return artists


def get_count_of_artists_faved(reload=False):
    redis = get_conn()
    key = 'artists_faved'
    count = redis.get(key)
    if count is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = """
                SELECT count(distinct(l.id, l.service))
                FROM lookup l
                INNER JOIN account_artist_favorite aaf
                    ON l.id = aaf.artist_id AND l.service = aaf.service
                WHERE aaf.service != 'discord-channel'
            """
            cursor.execute(query)
            count = cursor.fetchone()['count']
            redis.set(key, count, ex=3600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_count_of_artists_faved(reload=reload)
    else:
        count = int(count)
    return count


def get_random_artist_keys(count, reload=False):
    redis = get_conn()
    key = 'random_artist_keys:' + str(count)
    artist_keys = redis.get(key)
    if artist_keys is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = "SELECT id, service FROM lookup WHERE service != 'discord-channel' ORDER BY random() LIMIT %s"
            cursor.execute(query, (count,))
            artist_keys = cursor.fetchall()
            redis.set(key, ujson.dumps(artist_keys), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_random_artist_keys(count, reload=reload)
    else:
        artist_keys = ujson.loads(artist_keys)
    return artist_keys


def get_non_discord_artist_keys(reload=False):
    redis = get_conn()
    key = 'non_discord_artist_keys'
    artist_keys = redis.get(key)
    if artist_keys is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = "SELECT id, service FROM lookup WHERE service != 'discord-channel'"
            cursor.execute(query)
            artist_keys = cursor.fetchall()
            redis.set(key, ujson.dumps(artist_keys), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_non_discord_artist_keys(reload=reload)
    else:
        artist_keys = ujson.loads(artist_keys)
    return artist_keys


def get_all_non_discord_artists(reload=False):
    redis = get_conn()
    key = 'non_discord_artists'
    artists = redis.get(key)
    if artists is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = "SELECT * FROM lookup WHERE service != 'discord-channel'"
            cursor.execute(query)
            artists = cursor.fetchall()
            redis.set(key, serialize_artists(artists), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_all_non_discord_artists(reload=reload)
    else:
        artists = deserialize_artists(artists)
    return artists


def get_artists_by_service(service, reload=False):
    redis = get_conn()
    key = 'artists_by_service:' + service
    artists = redis.get(key)
    if artists is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = "SELECT * FROM lookup WHERE service = %s"
            cursor.execute(query, (service,))
            artists = cursor.fetchall()
            redis.set(key, serialize_artists(artists), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_artists_by_service(service, reload=reload)
    else:
        artists = deserialize_artists(artists)
    return artists


def get_artist(service: str, artist_id: str, reload: bool = False) -> dict:
    redis = get_conn()
    key = 'artist:' + service + ':' + str(artist_id)
    artist = redis.get(key)
    if artist is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = 'SELECT * FROM lookup WHERE id = %s AND service = %s'
            cursor.execute(query, (artist_id, service,))
            artist = cursor.fetchone()
            redis.set(key, serialize_artist(artist), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_artist(service, artist_id, reload=reload)
    else:
        artist = deserialize_artist(artist)
    return artist


def get_artist_post_count(service, artist_id, reload=False):
    redis = get_conn()
    key = 'artist_post_count:' + service + ':' + str(artist_id)
    count = redis.get(key)
    if count is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = 'SELECT count(*) as count FROM posts WHERE \"user\" = %s AND service = %s'
            cursor.execute(query, (artist_id, service,))
            count = cursor.fetchone()['count']
            redis.set(key, str(count), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_artist_post_count(service, artist_id, reload=reload)
    else:
        count = int(count)
    return count


def get_artist_last_updated(service, artist_id, reload=False):
    redis = get_conn()
    key = 'artist_last_updated:' + service + ':' + str(artist_id)
    last_updated = redis.get(key)
    if last_updated is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = 'SELECT max(added) as max FROM posts WHERE service = %s AND "user" = %s'
            cursor.execute(query, (service, artist_id,))
            last_updated = cursor.fetchone()
            if get_value(last_updated, 'max') is not None:
                last_updated = last_updated['max']
            else:
                last_updated = datetime.datetime.min
            redis.set(key, last_updated.isoformat(), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            get_artist_last_updated(service, artist_id, reload=reload)
    else:
        last_updated = dateutil.parser.parse(last_updated)

    return last_updated


def get_artists_by_update_time(offset, reload=False):
    redis = get_conn()
    key = 'artists_by_update_time:' + str(offset)
    artists = redis.get(key)
    if artists is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = "SELECT * FROM lookup WHERE service != 'discord-channel' ORDER BY updated desc "
            params = ()
            query += "OFFSET %s "
            params += (offset,)
            query += "LIMIT 25"
            cursor.execute(query, (params,))
            artists = cursor.fetchall()
            redis.set(key, serialize_artists(artists), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            get_artists_by_update_time(offset, reload=reload)
    else:
        artists = deserialize_artists(artists)
    return artists


def serialize_artists(artists):
    artists = copy.deepcopy(artists)
    return ujson.dumps(list(map(lambda artist: prepare_artist_fields(artist), artists)))


def deserialize_artists(artists_str):
    artists = ujson.loads(artists_str)
    return list(map(lambda artist: rebuild_artist_fields(artist), artists))


def serialize_artist(artist):
    if artist is not None:
        artist = prepare_artist_fields(copy.deepcopy(artist))
    return ujson.dumps(artist)


def deserialize_artist(artist_str):
    artist = ujson.loads(artist_str)
    if artist is not None:
        artist = rebuild_artist_fields(artist)
    return artist


def prepare_artist_fields(artist):
    artist['indexed'] = artist['indexed'].isoformat()
    artist['updated'] = artist['updated'].isoformat()
    return artist


def rebuild_artist_fields(artist):
    artist['indexed'] = dateutil.parser.parse(artist['indexed'])
    artist['updated'] = dateutil.parser.parse(artist['updated'])
    return artist
