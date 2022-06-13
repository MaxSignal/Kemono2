from typing import List, Optional, TypedDict

from ujson import dumps

from src.database import get_cursor
from src.internals.cache.redis import (
    deserialize_dict_list,
    get_conn,
    serialize_dict_list
)
from src.types.account import Notification


def count_account_notifications(account_id: int) -> int:
    """
    TODO: fix `psycopg2.ProgrammingError: no results to fetch` error
    """
    try:
        args_dict = {
            "account_id": account_id
        }

        cursor = get_cursor()
        query = """
            SELECT
                COUNT(*) AS notifications_count
            FROM notifications
            WHERE account_id = %(account_id)s
        """
        cursor.execute(query, args_dict)
        result = cursor.fetchone()
        notifications_count = result["notifications_count"]
        return notifications_count
    except:
        return 0


def count_new_notifications(account_id: int) -> int:
    """
    TODO: fix `psycopg2.ProgrammingError: no results to fetch` error
    """
    try:
        args_dict = dict(
            account_id=account_id
        )

        cursor = get_cursor()
        query = """
            SELECT
                COUNT(*) as new_notifications_count
            FROM notifications
            WHERE
                account_id = %(account_id)s
                AND is_seen = FALSE
        """
        cursor.execute(query, args_dict)
        # doing this to avoid `psycopg2.ProgrammingError: no results to fetch` error
        if not cursor.rowcount:
            return 0
        result = cursor.fetchone()
        new_notifications_count: int = result["new_notifications_count"]
        return new_notifications_count
    except:
        return 0


def set_notifications_as_seen(notification_ids: List[int]) -> bool:
    args_dict = dict(
        notification_ids=notification_ids
    )

    cursor = get_cursor()
    query = """
        UPDATE notifications
        SET is_seen = TRUE
        WHERE id = ANY (%(notification_ids)s)
    """
    cursor.execute(query, args_dict)

    return True


def get_account_notifications(account_id: int, reload: bool = False) -> List[Notification]:
    redis = get_conn()
    key = f"notifications_for_account:{account_id}"
    notifications = redis.get(key)
    result = None

    if notifications is None or reload:
        args_dict = dict(
            account_id=account_id
        )

        cursor = get_cursor()
        query = """
            SELECT id, account_id, type, created_at, is_seen, extra_info
            FROM notifications
            WHERE account_id = %(account_id)s
            ORDER BY
                created_at DESC
        """
        cursor.execute(query, args_dict)
        result = cursor.fetchall()
        redis.set(key, serialize_dict_list(result), ex=60)
    else:
        result = deserialize_dict_list(notifications)
    # TODO: fix this mess
    notifications = [Notification.from_dict(notification) for notification in result]
    return notifications


def send_notifications(
    account_ids: List[str],
    notification_type: int,
    extra_info: Optional[TypedDict]
) -> bool:
    cursor = get_cursor()
    if not account_ids:
        return False

    if extra_info is not None:
        extra_info = dumps(extra_info)
        notification_values = f"(%s, {notification_type}, '{extra_info}')"
    else:
        notification_values = f"(%s, {notification_type}, NULL)"

    insert_queries_values_template = ",".join([notification_values] * len(account_ids))
    insert_query = f"""
        INSERT INTO notifications (account_id, type, extra_info)
        VALUES {insert_queries_values_template}
        ;
        """
    cursor.execute(insert_query, account_ids)

    return True
