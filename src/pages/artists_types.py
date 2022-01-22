from dataclasses import dataclass
from typing import Callable, Dict, List

from src.types.kemono import Approved_DM
from src.internals.types import PageProps


@dataclass
class ArtistPageProps(PageProps):
    currentPage = "posts"
    id: str
    service: str
    session: Dict
    name: str
    count: int
    limit: int
    favorited: bool
    artist: Dict
    display_data: Callable[[Dict], Dict[str, str]]
    dm_count: int


@dataclass
class ArtistDMsProps(PageProps):
    currentPage = "dms"
    id: str
    service: str
    session: Dict
    artist: Dict
    display_data: Callable[[Dict], Dict[str, str]]
    dms: List[Approved_DM]
