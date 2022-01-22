from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from src.internals.types import DatabaseEntry


@dataclass
class Unapproved_DM(DatabaseEntry):
    """
    The DM which is shown to the importing user.
    """
    id: str
    user: str
    import_id: str
    contributor_id: str
    service: str
    content: str
    embed: Dict
    file: Dict
    added: datetime
    published: datetime


@dataclass
class Approved_DM(DatabaseEntry):
    """
    The public visible DM.
    """
    id: str
    user: str
    service: str
    content: str
    embed: Dict
    file: Dict
    added: datetime
    published: datetime

# class __Post:
#     id: str
#     user: str
#     service: str
#     added: datetime
#     published: datetime
#     edited: datetime
#     file: dict
#     attachments: list[dict]
#     title: str
#     content: str
#     embed: dict
#     shared_file: bool


class User:
    def __init__(self,
                 id: str,
                 name: str,
                 service: str,
                 indexed: datetime,
                 updated: datetime,
                 count: Optional[int]
                 ) -> None:
        self.id = id
        self.name = name
        self.service = service
        self.indexed = indexed
        self.updated = updated
        self.count = count if count else None

# class __Favorite_Post:
#     id: str
#     account_id: str
#     service: str
#     artist_id: str
#     post_id: str

# class __Favorite_User:
#     id: str
#     account_id: str
#     service: str
#     artist_id: str

# class __Request:
#     id: str
#     service: str
#     user: str
#     post_id: str
#     title: str
#     description: str
#     created: datetime
#     image: str
#     price: float
#     votes: int
#     ips: str
#     status: str

# class __Log:
#     log0: str
#     log: list[str]
#     created: datetime
