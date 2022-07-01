from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from src.internals.types import DatabaseEntry
# from typing import Optional, Union, Literal
# from packaging.version import parse as parse_version


IAccountRoles = Literal['consumer', 'moderator', 'administrator']
account_roles = ['consumer', 'moderator', 'administrator']
visible_roles = account_roles[:-1]


@dataclass
class Account(DatabaseEntry):
    id: int
    username: str
    created_at: datetime
    role: IAccountRoles
