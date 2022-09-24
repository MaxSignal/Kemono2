from ..internals.cache.redis import get_conn, KemonoRedisLock
from ..internals.database.database import get_cursor
import ujson
import redis_lock
import dateutil
import datetime
import copy
import re
import time


def get_random_posts_keys(count, reload=False):
    redis = get_conn()
    key = 'random_post_keys:' + str(count)
    post_keys = redis.get(key)
    if post_keys is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = "SELECT id, \"user\", service FROM posts WHERE file != '{}' AND attachments != '{}' ORDER BY random() LIMIT %s"
            cursor.execute(query, (count,))
            post_keys = cursor.fetchall()
            redis.set(key, ujson.dumps(post_keys), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_random_posts_keys(count, reload=reload)
    else:
        post_keys = ujson.loads(post_keys)
    return post_keys


def get_all_post_keys(reload=False):
    redis = get_conn()
    key = 'all_post_keys'
    post_keys = redis.get(key)
    if post_keys is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = "SELECT id, \"user\", service FROM posts"
            cursor.execute(query)
            post_keys = cursor.fetchall()
            redis.set(key, ujson.dumps(post_keys), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_all_post_keys(reload=reload)
    else:
        post_keys = ujson.loads(post_keys)
    return post_keys


def get_post(post_id, artist_id, service, reload=False):
    redis = get_conn()
    key = 'post:' + service + ':' + str(artist_id) + ':' + str(post_id)
    post = redis.get(key)
    if post is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = """
                SELECT *
                FROM (
                    SELECT *,
                        LAG(id)  OVER (ORDER BY published DESC, id ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) as prev,
                        LEAD(id) OVER (ORDER BY published DESC, id ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) as next
                    FROM posts
                    WHERE
                        "user" = %(artist_id)s
                        AND service = %(service)s
                        AND ("user", service) NOT IN (SELECT id, service from dnp)
                ) x
                WHERE %(post_id)s IN (id) ;
            """
            cursor.execute(query, dict(
                artist_id=artist_id,
                post_id=post_id,
                service=service
            ))
            post = cursor.fetchone()
            redis.set(key, serialize_post(post), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_post(post_id, artist_id, service, reload=reload)
    else:
        post = deserialize_post(post)
    return post


def get_post_comments(post_id, service, reload=False):
    redis = get_conn()
    key = 'comments:' + service + ':' + str(post_id)
    comments = redis.get(key)
    if comments is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = 'SELECT * FROM comments WHERE post_id = %s AND service = %s'
            cursor.execute(query, (post_id, service))
            comments = cursor.fetchall()
            redis.set(key, serialize_comments(comments), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_post_comments(post_id, service, reload=reload)
    else:
        comments = deserialize_comments(comments)
    return comments


def get_all_posts_by_artist(artist_id, service, reload=False):
    redis = get_conn()
    key = 'posts_by_artist:' + service + ':' + str(artist_id)
    posts = redis.get(key)
    if posts is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = """
                SELECT *
                FROM posts
                WHERE
                    "user" = %s
                    AND service = %s
                    AND ("user", service) NOT IN (SELECT id, service from dnp);
            """
            cursor.execute(query, (artist_id, service))
            posts = cursor.fetchall()
            redis.set(key, serialize_posts(posts), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_all_posts_by_artist(artist_id, service, reload=reload)
    else:
        posts = deserialize_posts(posts)
    return posts


def get_artist_posts(artist_id, service, offset, limit, sort='id', reload=False):
    redis = get_conn()
    key = 'artist_posts_offset:' + service + ':' + str(artist_id) + ':' + str(offset)
    posts = redis.get(key)
    if posts is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = 'SELECT * FROM posts WHERE \"user\" = %s AND service = %s ORDER BY ' + sort + ' OFFSET %s LIMIT %s'
            cursor.execute(query, (artist_id, service, offset, limit,))
            posts = cursor.fetchall()
            redis.set(key, serialize_posts(posts), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_artist_posts(artist_id, service, offset, limit, sort=sort, reload=reload)
    else:
        posts = deserialize_posts(posts)
    return posts


def is_post_flagged(service, artist_id, post_id, reload=False):
    redis = get_conn()
    key = 'is_post_flagged:' + service + ':' + str(artist_id) + ':' + str(post_id)
    flagged = redis.get(key)
    if flagged is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = "SELECT * FROM booru_flags WHERE id = %s AND \"user\" = %s AND service = %s"
            cursor.execute(query, (post_id, artist_id, service,))
            flagged = cursor.fetchone() is not None
            redis.set(key, str(flagged), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return is_post_flagged(service, artist_id, post_id, reload=reload)
    else:
        flagged = flagged.decode('utf-8') == 'True'
    return flagged


def get_next_post_id(post_id, artist_id, service, reload=False):
    redis = get_conn()
    key = 'next_post:' + service + ':' + str(artist_id) + ':' + str(post_id)
    next_post = redis.get(key)
    if next_post is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = """
                SELECT id
                FROM posts
                WHERE
                    posts.user = %s
                    AND service = %s
                    AND published < (
                        SELECT published
                        FROM posts
                        WHERE
                            id = %s
                            AND "user" = %s
                            AND service = %s
                        LIMIT 1
                    )
                ORDER BY published DESC
                LIMIT 1
            """
            cursor.execute(query, (artist_id, service, post_id, artist_id, service))
            next_post = cursor.fetchone()
            if next_post is None:
                next_post = ""
            else:
                next_post = next_post['id']
            redis.set(key, str(next_post), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_next_post_id(post_id, artist_id, service, reload=reload)
    else:
        next_post = next_post.decode('utf-8')

    if next_post == "":
        return None
    else:
        return next_post


def get_previous_post_id(post_id, artist_id, service, reload=False):
    redis = get_conn()
    key = 'previous_post:' + service + ':' + str(artist_id) + ':' + str(post_id)
    prev_post = redis.get(key)
    if prev_post is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            query = """
                SELECT id
                FROM posts
                WHERE
                    posts.user = %s
                    AND service = %s
                    AND published > (
                        SELECT published
                        FROM posts
                        WHERE
                            id = %s
                            AND "user" = %s
                            AND service = %s
                        LIMIT 1
                    )
                ORDER BY published ASC
                LIMIT 1
            """
            cursor.execute(query, (artist_id, service, post_id, artist_id, service,))
            prev_post = cursor.fetchone()
            if prev_post is None:
                prev_post = ""
            else:
                prev_post = prev_post['id']
            redis.set(key, str(prev_post), ex=600)
            lock.release()
        else:
            time.sleep(0.1)
            return get_previous_post_id(post_id, artist_id, service, reload=reload)
    else:
        prev_post = prev_post.decode('utf-8')

    if prev_post == "":
        return None
    else:
        return prev_post


def get_render_data_for_posts(posts):
    result_previews = []
    result_attachments = []
    result_flagged = []
    result_after_kitsune = []
    result_is_image = []

    for post in posts:
        if post['added'] > datetime.datetime(2020, 12, 22, 0, 0, 0, 0):
            result_after_kitsune.append(True)
        else:
            result_after_kitsune.append(False)

        previews = []
        attachments = []
        if len(post['file']):
            if re.search("\.(gif|jpe?g|jpe|png|webp)$", post['file']['path'], re.IGNORECASE):  # noqa: W605
                result_is_image.append(True)
                previews.append({
                    'type': 'thumbnail',
                    'name': post['file'].get('name'),
                    'path': post['file']['path'].replace('https://kemono.party', '')
                })
            else:
                result_is_image.append(False)
                attachments.append({
                    'path': post['file']['path'].replace('https://kemono.party', ''),
                    'name': post['file'].get('name')
                })
        else:
            result_is_image.append(False)

        if len(post['embed']):
            previews.append({
                'type': 'embed',
                'url': post['embed']['url'],
                'subject': post['embed']['subject'],
                'description': post['embed']['description']
            })
        for attachment in post['attachments']:
            if re.search("\.(gif|jpe?g|jpe|png|webp)$", attachment['path'], re.IGNORECASE):  # noqa: W605
                previews.append({
                    'type': 'thumbnail',
                    'name': attachment.get('name'),
                    'path': attachment['path'].replace('https://kemono.party', '')
                })
            else:
                attachments.append({
                    'path': attachment['path'],
                    'name': attachment.get('name')
                })

        result_flagged.append(is_post_flagged(post['id'], post['user'], post['service']))
        result_previews.append(previews)
        result_attachments.append(attachments)

    return (result_previews, result_attachments, result_flagged, result_after_kitsune, result_is_image)


def serialize_posts(posts):
    posts = copy.deepcopy(posts)
    return ujson.dumps(list(map(lambda post: prepare_post_fields(post), posts)))


def deserialize_posts(posts_str):
    posts = ujson.loads(posts_str)
    return list(map(lambda post: rebuild_post_fields(post), posts))


def serialize_comments(comments):
    comments = copy.deepcopy(comments)
    return ujson.dumps(list(map(lambda post: prepare_comment_fields(post), comments)))


def deserialize_comments(comments_str):
    comments = ujson.loads(comments_str)
    return list(map(lambda post: rebuild_comment_fields(post), comments))


def serialize_post(post):
    if post is not None:
        post = prepare_post_fields(copy.deepcopy(post))
    return ujson.dumps(post)


def deserialize_post(post_str):
    post = ujson.loads(post_str)
    if post is not None:
        post = rebuild_post_fields(post)
    return post


def prepare_post_fields(post):
    post['added'] = post['added'].isoformat()
    post['published'] = post['published'].isoformat() if post['published'] else None
    post['edited'] = post['edited'].isoformat() if post['edited'] else None
    return post


def rebuild_post_fields(post):
    post['added'] = dateutil.parser.parse(post['added'])
    post['published'] = dateutil.parser.parse(post['published']) if post['published'] else None
    post['edited'] = dateutil.parser.parse(post['edited']) if post['edited'] else None
    return post


def prepare_comment_fields(comment):
    comment['added'] = comment['added'].isoformat()
    comment['published'] = comment['published'].isoformat() if comment['published'] else None
    return comment


def rebuild_comment_fields(comment):
    comment['added'] = dateutil.parser.parse(comment['added'])
    comment['published'] = dateutil.parser.parse(comment['published']) if comment['published'] else None
    return comment
