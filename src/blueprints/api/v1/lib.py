import time
from typing import List, Union

from flask import Request

from src.internals.cache.redis import (
    KemonoRedisLock,
    create_counts_key_constructor,
    create_key_constructor,
    deserialize_dict_list,
    get_conn,
    serialize_dict_list
)
from src.database import get_cursor
from src.utils.utils import paysite_list, encode_text_query

from .types import (
    TDArtist,
    TDArtistsParams,
    TDPaginationDB,
    TDValidationFailure,
    TDValidationSuccess
)

construct_artists_key = create_key_constructor("artists")
construct_artists_count_key = create_counts_key_constructor("artists")
construct_banned_artists_key = create_key_constructor("banned_artists")
construct_banned_artists_count_key = create_counts_key_constructor("banned_artists")

available_params = frozenset(("service", "sort_by"))
default_sort = "updated"
default_params = TDArtistsParams(
    service=None,
    sort_by=default_sort
)

sort_queries = dict(
    updated=",\n".join(("updated ASC", "name ASC", "service ASC")),
    added=",\n".join(("indexed ASC", "name ASC", "service ASC")),
    name=",\n".join(("name ASC", "service ASC", "indexed ASC")),
    service=",\n".join(("service ASC", "name ASC", "indexed ASC"))
)
sort_fields = sort_queries.keys()


def validate_artists_request(req: Request) -> Union[TDValidationFailure, TDValidationSuccess]:
    errors = []
    args_dict = req.args.to_dict()
    service = args_dict.get("service", "").strip()
    # name = args_dict.get("name", "").strip()
    sort_by = args_dict.get("sort_by", default_sort).strip()

    is_valid_params = len(args_dict) <= len(available_params)

    if (not is_valid_params):
        errors.append(f"Only {', '.join(available_params)} params allowed.")

    if (service and service not in paysite_list):
        errors.append("Not a valid service.")

    if (sort_by not in sort_fields):
        errors.append("Not a valid sorting.")

    if (errors):
        result = TDValidationFailure(
            is_successful=False,
            errors=errors
        )

        return result

    validated_params = TDArtistsParams(
        sort_by=sort_by,
        service=service,
        # name=name
    )
    result = TDValidationSuccess(
        is_successful=True,
        data=validated_params
    )

    return result


def count_artists(
    service: str = None,
    # name: str = None,
    reload: bool = False
) -> int:
    redis = get_conn()
    # encoded_name = encode_text_query(name)
    redis_key = construct_artists_count_key(
        *("service", service) if service else "",
        # *("name", encoded_name) if name else ""
    )
    artist_count = redis.get(redis_key)
    result = None

    if artist_count and not reload:
        result = int(artist_count)
        return result

    lock = KemonoRedisLock(redis, redis_key, expire=60, auto_renewal=True)

    if not lock.acquire(blocking=False):
        time.sleep(0.1)
        return count_artists(
            service,
            # name,
            reload=reload
        )

    cursor = get_cursor()
    query_args = dict(
        service=service,
        # name=name
    )

    # name_query = f"AND to_tsvector('english', name) @@ websearch_to_tsquery(%(name)s)" if name else ""

    query = f"""
        SELECT COUNT(*) as artist_count
        FROM lookup
        WHERE
            service != 'discord-channel'
            {"AND service = %(service)s" if service else ""}
    """
    cursor.execute(query, query_args)
    result = cursor.fetchone()
    artist_count: int = result['artist_count']
    redis.set(redis_key, str(artist_count), ex=600)
    lock.release()

    return artist_count


def get_artists(
    pagination_db: TDPaginationDB,
    params: TDArtistsParams = default_params,
    reload: bool = False
) -> List[TDArtist]:
    """
    Get all artist information.
    @TODO return dataclass
    """
    redis = get_conn()
    service = params["service"]
    sort_by = params["sort_by"]
    # encoded_name = encode_text_query(params["name"])
    redis_key = construct_artists_key(
        *("service", service) if service else "",
        *("sort_by", sort_by),
        # *("name", encoded_name) if name else "",
        str(pagination_db["pagination_init"]["current_page"])
    )

    artists = redis.get(redis_key)

    if artists is not None and not reload:
        return deserialize_dict_list(artists)

    lock = KemonoRedisLock(redis, redis_key, expire=60, auto_renewal=True)

    if not lock.acquire(blocking=False):
        time.sleep(0.1)
        return get_artists(
            pagination_db,
            params,
            reload=reload
        )

    cursor = get_cursor()
    arg_dict = dict(
        offset=pagination_db["offset"],
        limit=pagination_db["sql_limit"],
        service=service,
        # name=name
    )
    # name_query = f"AND to_tsvector('english', name) @@ websearch_to_tsquery(%(name)s)" if name else ""
    sort_query = sort_queries[sort_by]

    query = f"""
        SELECT id, indexed, name, service, updated
        FROM lookup
        WHERE
            service != 'discord-channel'
            {
                "AND service = %(service)s"
                if service
                else ""
            }
        ORDER BY
            {sort_query}
        OFFSET %(offset)s
        LIMIT %(limit)s
    """
    cursor.execute(query, arg_dict)
    artists: List[TDArtist] = cursor.fetchall()
    redis.set(redis_key, serialize_dict_list(artists), ex=600)
    lock.release()

    return artists


def count_banned_artists(reload: bool = False) -> int:
    redis = get_conn()
    redis_key = construct_banned_artists_count_key()
    artist_count = redis.get(redis_key)
    result = None

    if artist_count and not reload:
        result = int(artist_count)
        return result

    lock = KemonoRedisLock(redis, redis_key, expire=60, auto_renewal=True)

    if not lock.acquire(blocking=False):
        time.sleep(0.1)

        return count_banned_artists(reload=reload)

    cursor = get_cursor()
    query = """
        SELECT COUNT(*) as artist_count
        FROM dnp
    """
    cursor.execute(query)
    result = cursor.fetchone()
    artist_count: int = result['artist_count']
    redis.set(redis_key, str(artist_count), ex=600)
    lock.release()

    return artist_count


def get_banned_artists(
    pagination_db: TDPaginationDB,
    reload: bool = False
):
    redis = get_conn()
    redis_key = construct_banned_artists_key(
        str(pagination_db["pagination_init"]["current_page"])
    )
    banned_artists = redis.get(redis_key)
    result = None

    if banned_artists is not None and not reload:
        result = deserialize_dict_list(banned_artists)
        return result

    lock = KemonoRedisLock(redis, redis_key, expire=60, auto_renewal=True)

    if not lock.acquire(blocking=False):
        time.sleep(0.1)

        return get_banned_artists(
            pagination_db,
            reload=reload,
        )

    cursor = get_cursor()
    query_args = dict(
        offset=pagination_db["offset"],
        limit=pagination_db["sql_limit"]
    )
    query = """
        SELECT
            artist.id,
            artist.indexed,
            artist.name,
            artist.service,
            artist.updated
        FROM
            dnp as banned,
            lookup as artist
        WHERE
            banned.id = artist.id
            AND banned.service = artist.service
        OFFSET %(offset)s
        LIMIT %(limit)s
    """
    cursor.execute(query, query_args)
    result: List[TDArtist] = cursor.fetchall()
    redis.set(redis_key, serialize_dict_list(banned_artists), ex=600)
    lock.release()

    return result
