from typing import List, Union

from flask import Request

from src.blueprints.api.v1.types import (
    TDValidationFailure,
    TDValidationSuccess
)
from src.utils.utils import is_valid_service

from .types import TDArtistBanAPIRequest


def validate_ban_api_request(request: Request) -> Union[TDValidationSuccess, TDValidationFailure]:
    """
    This is validating the json body therefore
    no type castings, formatting or mutations are performed.
    """
    errors: List[str] = []
    req_body: TDArtistBanAPIRequest = request.json
    service = req_body["data"]["service"]
    id = req_body["data"]["id"]

    if (not is_valid_service(service)):
        errors.append("Not a valid service.")

    if (not isinstance(id, str)):
        errors.append("Not a valid id.")

    if (errors):
        return TDValidationFailure(
            is_successful=False,
            errors=errors
        )

    return TDValidationSuccess(
        is_successful=True,
        data=req_body["data"]
    )
