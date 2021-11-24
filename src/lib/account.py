import ujson
import copy
import bcrypt
import base64
import hashlib
import dateutil
import redis_lock
from flask import session, current_app, flash
from threading import Lock
from bleach.sanitizer import Cleaner
from ..internals.database.database import get_cursor
from ..utils.utils import get_value
from ..internals.cache.redis import get_conn, serialize_dict_list, deserialize_dict_list, KemonoRedisLock
from ..lib.favorites import add_favorite_artist
from ..lib.artist import get_artist
from ..lib.security import is_login_rate_limited
from src.types.account import Account, Service_Key
from typing import Dict, List, Optional

account_create_lock = Lock()


def load_account(account_id: str = None, reload: bool = False):
    """
    TODO: Make it return an instance of `Account`.
    """
    if account_id is None and 'account_id' in session:
        return load_account(session['account_id'], reload)
    elif account_id is None and 'account_id' not in session:
        return None

    redis = get_conn()
    key = 'account:' + str(account_id)
    account = redis.get(key)
    if account is None or reload:
        cursor = get_cursor()
        query = """
            SELECT id, username, created_at, role
            FROM account
            WHERE id = %s
        """
        cursor.execute(query, (account_id,))
        account = cursor.fetchone()
        redis.set(key, serialize_account(account))
    else:
        account = deserialize_account(account)

    return account


def get_saved_key_import_ids(key_id, reload=False):
    redis = get_conn()
    key = 'saved_key_import_ids:' + str(key_id)
    saved_key_import_ids = redis.get(key)
    if saved_key_import_ids is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            # TODO: select columns
            query = """
                SELECT *
                FROM saved_session_key_import_ids
                WHERE key_id = %s
            """
            cursor.execute(query, (int(key_id),))
            saved_key_import_ids = cursor.fetchall()
            redis.set(key, serialize_dict_list(saved_key_import_ids), ex=3600)
            lock.release()
        else:
            return get_saved_key_import_ids(key_id, reload=reload)
    else:
        saved_key_import_ids = deserialize_dict_list(saved_key_import_ids)

    return saved_key_import_ids


def get_saved_keys(account_id: int, reload: bool = False):
    redis = get_conn()
    key = 'saved_keys:' + str(account_id)
    saved_keys = redis.get(key)
    result = None
    if saved_keys is None or reload:
        lock = KemonoRedisLock(redis, key, expire=60, auto_renewal=True)
        if lock.acquire(blocking=False):
            cursor = get_cursor()
            args_dict = dict(
                account_id=str(account_id)
            )
            query = """
                SELECT id, service, discord_channel_ids, added, dead
                FROM saved_session_keys_with_hashes
                WHERE contributor_id = %(account_id)s
                ORDER BY
                    added DESC
            """
            cursor.execute(query, args_dict)
            result = cursor.fetchall()
            redis.set(key, serialize_dict_list(result), ex=3600)
            lock.release()
        else:
            return get_saved_keys(account_id, reload=reload)
    else:
        result = deserialize_dict_list(saved_keys)
    saved_keys = [Service_Key.init_from_dict(service_key) for service_key in result]
    return saved_keys


def revoke_saved_keys(key_ids: List[int], account_id: int):
    cursor = get_cursor()
    query_args = dict(
        key_ids=key_ids,
        account_id=account_id
    )
    query1 = """
        DELETE
        FROM saved_session_key_import_ids skid
        USING saved_session_keys_with_hashes sk
        WHERE
            skid.key_id = sk.id
            AND sk.id = ANY (%(key_ids)s)
            AND sk.contributor_id = %(account_id)s
    """
    cursor.execute(query1, query_args)
    query2 = """
        DELETE
        FROM saved_session_keys_with_hashes
        WHERE
            id = ANY (%(key_ids)s)
            AND contributor_id = %(account_id)s
    """
    cursor.execute(query2, query_args)
    redis = get_conn()
    key = 'saved_keys:' + str(account_id)
    redis.delete(key)
    return True


def get_login_info_for_username(username):
    cursor = get_cursor()
    query = 'SELECT id, password_hash FROM account WHERE username = %s'
    cursor.execute(query, (username,))
    return cursor.fetchone()


def is_logged_in():
    if 'account_id' in session:
        return True
    return False


def is_username_taken(username):
    cursor = get_cursor()
    query = 'SELECT id FROM account WHERE username = %s'
    cursor.execute(query, (username,))
    return cursor.fetchone() is not None


def create_account(username: str, password: str, favorites: Optional[List[Dict]] = None) -> bool:
    account_id = None
    password_hash = bcrypt.hashpw(get_base_password_hash(password), bcrypt.gensalt()).decode('utf-8')
    account_create_lock.acquire()
    try:
        if is_username_taken(username):
            return False

        scrub = Cleaner(tags=[])

        cursor = get_cursor()
        query = """
            INSERT INTO account (username, password_hash)
            VALUES (%s, %s)
            RETURNING id
        """
        cursor.execute(query, (scrub.clean(username), password_hash,))
        account_id = cursor.fetchone()['id']
        if (account_id == 1):
            cursor = get_cursor()
            query = """
                UPDATE account
                SET role = 'administrator'
                WHERE id = 1
            """
            cursor.execute(query)
    finally:
        account_create_lock.release()

    if favorites is not None:
        for favorite in favorites:
            artist = get_artist(favorite['service'], favorite['artist_id'])
            if artist is None:
                continue
            add_favorite_artist(account_id, favorite['service'], favorite['artist_id'])

    return True


def attempt_login(username, password):
    if username is None or password is None:
        return False

    account_info = get_login_info_for_username(username)
    if account_info is None:
        flash('Username or password is incorrect')
        return False

    if get_value(current_app.config, 'ENABLE_LOGIN_RATE_LIMITING') and is_login_rate_limited(account_info['id']):
        flash('You\'re doing that too much. Try again in a little bit.')
        return False

    if bcrypt.checkpw(get_base_password_hash(password), account_info['password_hash'].encode('utf-8')):
        account = load_account(account_info['id'], True)
        session['account_id'] = account['id']
        return True

    flash('Username or password is incorrect')
    return False


def get_base_password_hash(password: str):
    return base64.b64encode(hashlib.sha256(password.encode('utf-8')).digest())


def serialize_account(account):
    account = copy.deepcopy(account)
    return ujson.dumps(prepare_account_fields(account))


def deserialize_account(account):
    account = ujson.loads(account)
    return rebuild_account_fields(account)


def prepare_account_fields(account):
    account['created_at'] = account['created_at'].isoformat()
    return account


def rebuild_account_fields(account):
    account['created_at'] = dateutil.parser.parse(account['created_at'])
    return account
