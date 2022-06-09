from datetime import datetime
from typing import Dict, List, Literal, Optional, TypedDict, Type

DEFAULT_PAGE_LIMIT = 25


class TDArtist(TypedDict):
    id: str
    indexed: datetime
    name: str
    service: str
    updated: datetime


class TDAPIRequest(TypedDict):
    """
    Base API request.
    For `GET` routes the keys are pulled from search params instead.
    """
    data: Optional[Dict]


class TDAPIResponseSuccess(TypedDict):
    """
    Base API response.
    """
    is_successful: Literal[True]
    data: Optional[Dict]


class TDAPIResponseFaillure(TypedDict):
    """
    `validation_errors` is a separate entity for use by forms.
    """
    is_successful: Literal[False]
    errors: List[str]


class TDArtistsParams(TypedDict):
    service: Optional[str]
    # name: Optional[str]


class TDValidationFailure(TypedDict):
    is_successful: Literal[False]
    errors: List[str]


class TDValidationSuccess(TypedDict):
    """
    TODO: Rewrite as a class with a generic.
    """
    is_successful: Literal[True]
    data: Optional[Dict]


class TDPaginationInit(TypedDict):
    current_page: int
    limit: int
    total_count: int
    total_pages: int


class TDPaginationDB(TypedDict):
    pagination_init: TDPaginationInit
    offset: int
    sql_limit: int


class TDPagination(TypedDict):
    total_count: int
    total_pages: int
    current_page: int
    limit: int


class TDArtistResponse(TypedDict):
    pagination: TDPagination
    artists: List[TDArtist]
