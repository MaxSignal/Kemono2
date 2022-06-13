from typing import Dict, List

from src.internals.database.database import get_cursor
from src.lib.account import TDAccount
from src.lib.notification import send_notifications
from src.lib.pagination import Pagination
from src.types.account import ACCOUNT_ROLE_CHANGE, Account, Notification_Types


def is_administrator(account: TDAccount):
    if (account["role"] != "administrator"):
        return False

    return True


def get_account(account_id: str) -> Account:
    cursor = get_cursor()
    query = """
        SELECT id, username, created_at, role
        FROM account
        WHERE id = %s
        """
    cursor.execute(query, (account_id))
    account = cursor.fetchone()
    account = Account.init_from_dict(account)

    return account


def count_accounts(queries: Dict[str, str]) -> int:

    arg_dict = {
        'role': queries['role'],
        'username': f"%%{queries['name']}%%" if queries.get('name') is not None else None
    }

    cursor = get_cursor()
    query = f"""
        SELECT COUNT(*) AS total_number_of_accounts
        FROM account
        WHERE
            role = ANY(%(role)s)
            {'AND username LIKE %(username)s' if queries.get('name') is not None else ''}
    """
    cursor.execute(query, arg_dict)
    result = cursor.fetchone()
    number_of_accounts = result['total_number_of_accounts']
    return number_of_accounts


def get_accounts(pagination: Pagination, queries: Dict[str, str]) -> List[Account]:

    arg_dict = {
        'role': queries['role'],
        'offset': pagination.offset,
        'limit': pagination.limit,
        'username': f"%%{queries['name']}%%" if queries.get('name') is not None else None
    }

    cursor = get_cursor()
    query = f"""
        SELECT id, username, created_at, role
        FROM account
        WHERE
            role = ANY(%(role)s)
            {'AND username LIKE %(username)s' if queries.get('name') is not None else ''}
        ORDER BY
            created_at DESC,
            username
        OFFSET %(offset)s
        LIMIT %(limit)s
    """
    cursor.execute(query, arg_dict)
    accounts = cursor.fetchall()
    accList = [Account.init_from_dict(acc) for acc in accounts]

    count = count_accounts(queries)
    pagination.add_count(count)

    return accList


def change_account_role(
    account_ids: List[str],
    extra_info: ACCOUNT_ROLE_CHANGE
):
    cursor = get_cursor()
    arg_dict = dict(
        account_ids=account_ids,
        new_role=extra_info["new_role"]
    )

    change_role_query = """
        UPDATE account
        SET role = %(new_role)s
        WHERE id = ANY (%(account_ids)s)
    """
    cursor.execute(change_role_query, arg_dict)

    send_notifications(
        account_ids,
        Notification_Types.ACCOUNT_ROLE_CHANGE,
        extra_info
    )

    return True
