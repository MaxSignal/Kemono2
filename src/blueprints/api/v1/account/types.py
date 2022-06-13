from typing import TypedDict

from src.types.account.account import IAccountRoles


class TDAccountInfo(TypedDict):
    role: IAccountRoles
