import time

from src.database.lib import get_cursor
from src.lib.cache import (
    KemonoRedisLock,
    deserialize_dict_list,
    get_conn,
    serialize_dict_list
)


def count_all_posts(reload=False):
    redis = get_conn()
    key = 'global_post_count'
    count = redis.get(key)
    if count is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = 'SELECT COUNT(*) FROM posts'
            cursor.execute(query)
            count = cursor.fetchone()
            redis.set(key, str(count['count']), ex=600)
            count = int(count['count'])
            lock.release()
        else:
            time.sleep(0.1)
            return count_all_posts(reload=reload)
    else:
        count = int(count)
    return count


def count_all_posts_for_query(q: str, reload=False):
    if q.strip() == '':
        return count_all_posts()
    redis = get_conn()
    key = 'global_post_count_for_query:' + q
    count = redis.get(key)
    if count is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = "SELECT COUNT(*) FROM posts WHERE to_tsvector('english', content || ' ' || title) @@ websearch_to_tsquery(%s)"
            cursor.execute(query, (q,))
            count = cursor.fetchone()
            redis.set(key, str(count['count']), ex=600)
            count = int(count['count'])
            lock.release()
        else:
            time.sleep(0.1)
            return count_all_posts_for_query(q, reload=reload)
    else:
        count = int(count)
    return count


def get_all_posts(offset: int, reload=False):
    redis = get_conn()
    key = 'all_posts:' + str(offset)
    all_posts = redis.get(key)
    if all_posts is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = 'SELECT * FROM posts ORDER BY added desc OFFSET %s LIMIT 25'
            cursor.execute(query, (offset,))
            all_posts = cursor.fetchall()
            redis.set(key, serialize_dict_list(all_posts), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_all_posts(offset, reload=reload)
    else:
        all_posts = deserialize_dict_list(all_posts)
    return all_posts


def get_all_posts_for_query(q: str, offset: int, reload=False):
    if q.strip() == '':
        return get_all_posts(0)
    redis = get_conn()
    key = 'all_posts_for_query:' + q + ':' + str(offset)
    results = redis.get(key)
    if results is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = "SET LOCAL enable_indexscan = off; "
            query += "SELECT * FROM posts WHERE to_tsvector('english', content || ' ' || title) @@ websearch_to_tsquery(%s) ORDER BY added desc LIMIT 25 OFFSET %s"
            params = (q, offset)

            cursor.execute(query, params)
            results = cursor.fetchall()
            redis.set(key, serialize_dict_list(results), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_all_posts_for_query(q, offset, reload=reload)
    else:
        results = deserialize_dict_list(results)
    return results
