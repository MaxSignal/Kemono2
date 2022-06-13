from typing import TypedDict
from src.blueprints.api.v1.types import TDAPIRequest


class TDBanData(TypedDict):
    service: str
    id: str


class TDArtistBanAPIRequest(TDAPIRequest):
    data: TDBanData
