import base64
import copy
import time
from typing import List

import dateutil
import ujson

from src.internals.cache.redis import KemonoRedisLock, get_conn
from src.internals.database.database import get_cursor
from src.types.kemono import Approved_DM, Unapproved_DM


def get_unapproved_dms(import_id: str, account_id: int, reload: bool = False) -> List[Unapproved_DM]:
    """
    TODO: fix `account_id` type
    """
    redis = get_conn()
    key = f'unapproved_dms:{import_id}:{str(account_id)}'
    dms = redis.get(key)
    result = None

    if dms and not reload:
        result = deserialize_dms(dms)
        return [Unapproved_DM.init_from_dict(dm) for dm in result] if result else []

    lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)

    if not lock.acquire(blocking=False):
        time.sleep(0.1)
        return get_unapproved_dms(import_id, account_id, reload=reload)

    cursor = get_cursor()
    args_dict = dict(
        import_id=import_id,
        account_id=str(account_id)
    )
    query = """
        SELECT
            id, import_id, contributor_id, "user", service, content, embed, added, published, file
        FROM unapproved_dms
        WHERE
            import_id = %(import_id)s
            AND contributor_id = %(account_id)s
    """
    cursor.execute(query, args_dict)
    result = cursor.fetchall()
    redis.set(key, serialize_dms(result), ex=1)
    lock.release()

    dms = [Unapproved_DM.init_from_dict(dm) for dm in result] if result else []

    return dms


def count_user_dms(service: str, user_id: str, reload: bool = False) -> int:
    redis = get_conn()
    key = f"dms_count:{service}:{user_id}"
    count = redis.get(key)

    if count and not reload:
        return int(count)

    lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)

    if not lock.acquire(blocking=False):
        time.sleep(0.1)
        return count_user_dms(service, user_id, reload=reload)

    cursor = get_cursor()
    query_args = dict(
        service=service,
        user_id=user_id
    )
    query = """
        SELECT COUNT(*)
        FROM dms
        WHERE
            service = %(service)s
            AND "user" = %(user_id)s

    """
    cursor.execute(query, query_args)
    result = cursor.fetchall()
    count = result[0]['count']
    redis.set(key, str(count), ex=600)
    lock.release()

    return count


def get_artist_dms(service: str, artist_id: int, reload: bool = False) -> List[Approved_DM]:
    redis = get_conn()
    key = f'dms:{service}:{str(artist_id)}'
    dms = redis.get(key)
    result = None

    if dms and not reload:
        result = deserialize_dms(dms)
        return [Approved_DM.init_from_dict(dm) for dm in result] if result else []

    lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)

    if not lock.acquire(blocking=False):
        time.sleep(0.1)
        return get_artist_dms(service, artist_id, reload=reload)

    cursor = get_cursor()
    query_args = dict(
        service=service,
        artist_id=artist_id
    )
    query = """
        SELECT
            id, "user", service, content, embed, file, added, published
        FROM dms
        WHERE
            service = %(service)s
            AND "user" = %(artist_id)s
    """
    cursor.execute(query, query_args)
    result = cursor.fetchall()
    redis.set(key, serialize_dms(result), ex=600)
    lock.release()

    dms = [Approved_DM.init_from_dict(dm) for dm in result] if result else []

    return dms


def get_all_dms_count(reload: bool = False) -> int:
    redis = get_conn()
    key = 'all_dms_count'
    count = redis.get(key)

    if count and not reload:
        return int(count)

    lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)

    if not lock.acquire(blocking=False):
        time.sleep(0.1)
        return get_all_dms_count(reload=reload)

    cursor = get_cursor()
    query = """
        SELECT COUNT(*)
        FROM dms
    """
    cursor.execute(query)
    count = int(cursor.fetchone()['count'])
    redis.set(key, str(count), ex=600)
    lock.release()

    return count


def get_all_dms(offset: int, limit: int, reload: bool = False) -> List[Approved_DM]:
    redis = get_conn()
    key = f'all_dms:{str(offset)}'
    dms = redis.get(key)
    result = None

    if dms and not reload:
        result = deserialize_dms(dms)
        return [Approved_DM.init_from_dict(dm) for dm in result] if result else []

    lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)

    if not lock.acquire(blocking=False):
        time.sleep(0.1)
        return get_all_dms(offset, limit, reload=reload)

    cursor = get_cursor()
    query_args = dict(
        offset=offset,
        limit=limit
    )
    query = """
        SELECT
            id, "user", service, content, embed, file, added, published
        FROM dms
        ORDER BY
            added DESC
        OFFSET %(offset)s
        LIMIT %(limit)s
    """
    cursor.execute(query, query_args)
    result = cursor.fetchall()
    redis.set(key, serialize_dms(result), ex=600)
    lock.release()

    dms = [Approved_DM.init_from_dict(dm) for dm in result] if result else []

    return dms


def get_all_dms_by_query_count(text_query: str, reload: bool = False) -> int:
    redis = get_conn()
    key = 'all_dms_by_query_count:' + base64.b64encode(text_query.encode('utf-8')).decode('utf-8')
    count = redis.get(key)

    if count and not reload:
        return int(count)

    lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)

    if not lock.acquire(blocking=False):
        time.sleep(0.1)
        return get_all_dms_by_query_count(text_query, reload=reload)

    cursor = get_cursor()
    query_args = dict(
        text_query=text_query
    )
    query = 'SET random_page_cost = 0.0001; SET LOCAL statement_timeout = 10000; '
    query += 'SELECT COUNT(*) FROM dms WHERE content &@~ %(text_query)s'
    cursor.execute(query, query_args)
    count = int(cursor.fetchone()['count'])
    redis.set(key, str(count), ex=600)
    lock.release()

    return count


def get_all_dms_by_query(
    text_query: str,
    offset: int,
    limit: int,
    reload: bool = False
) -> List[Approved_DM]:
    transformed_query = base64.b64encode(text_query.encode('utf-8')).decode('utf-8')
    redis = get_conn()
    key = f'all_dms_by_query:{transformed_query}:{str(offset)}'
    dms = redis.get(key)
    result = None

    if dms and not reload:
        result = deserialize_dms(dms)
        return [Approved_DM.init_from_dict(dm) for dm in result] if result else []

    lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
    if not lock.acquire(blocking=False):
        time.sleep(0.1)
        return get_all_dms_by_query(text_query, offset, limit, reload=reload)

    cursor = get_cursor()
    query_args = dict(
        text_query=text_query,
        offset=offset,
        limit=limit
    )
    query = """
        SELECT
            id, "user", service, content, embed, file, added, published
        FROM dms
        WHERE
            to_tsvector(\'english\', content) @@ websearch_to_tsquery(%(text_query)s)
        ORDER BY
            added DESC
        OFFSET %(offset)s
        LIMIT %(limit)s
    """
    cursor.execute(query, query_args)
    result = cursor.fetchall()
    redis.set(key, serialize_dms(result), ex=600)
    lock.release()

    dms = [Approved_DM.init_from_dict(dm) for dm in result] if result else []

    return dms


def cleanup_unapproved_dms(import_id: str):
    cursor = get_cursor()
    query_args = dict(
        import_id=import_id
    )
    query = """
        DELETE
        FROM unapproved_dms
        WHERE import_id = %(import_id)s
    """
    cursor.execute(query, query_args)

    return True


def approve_dm(import_id: str, dm_id: str):
    cursor = get_cursor()
    query_args = dict(
        import_id=import_id,
        dm_id=dm_id
    )
    query = """
        INSERT INTO
            dms (id, "user", service, content, embed, added, published, file)
        SELECT
            id, "user", service, content, embed, added, published, file
        FROM unapproved_dms
        WHERE
            import_id = %(import_id)s
            AND id = %(dm_id)s
        ;
        DELETE
            FROM unapproved_dms
        WHERE
            import_id = %(import_id)s
            AND id = %(dm_id)s
        ;
    """
    cursor.execute(query, query_args)

    return True


def serialize_dms(dms):
    dms = copy.deepcopy(dms)
    return ujson.dumps(list(map(lambda dm: prepare_dm_fields(dm), dms)))


def deserialize_dms(dms_str):
    dms = ujson.loads(dms_str)
    return list(map(lambda dm: rebuild_dm_fields(dm), dms))


def rebuild_dm_fields(dm):
    dm['added'] = dateutil.parser.parse(dm['added'])
    dm['published'] = dateutil.parser.parse(dm['published'])
    return dm


def prepare_dm_fields(dm):
    dm['added'] = dm['added'].isoformat()
    dm['published'] = dm['published'].isoformat()
    return dm
