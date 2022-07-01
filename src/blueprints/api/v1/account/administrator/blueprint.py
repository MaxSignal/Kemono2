import logging
from flask import Blueprint, jsonify, make_response, request

from src.blueprints.api.v1.types import TDAPIResponseFailure, TDAPIResponseSuccess
from src.lib.artist import ban_artist, unban_artist
from src.lib.account import TDAccount, load_account
from src.lib.administrator import is_administrator

from .lib import validate_ban_api_request
from .types import TDBanData

administrator_api = Blueprint('administrator', __name__, url_prefix='/administrator')


@administrator_api.before_request
def get_account_creds():
    account: TDAccount = load_account()

    if (is_administrator(account)):
        return

    log_message = f"Account with ID of \"{account['id']}\" and role \"{account['role']}\" tried to access administrator API."
    logging.warn(log_message)

    errors = ["Not Found"]
    api_response = TDAPIResponseFailure(
        is_successful=False,
        errors=errors
    )
    response = make_response(jsonify(api_response), 404)

    return response


@administrator_api.put("/bans")
def artist_ban():
    result = validate_ban_api_request(request)

    if (not result['is_successful']):
        api_response = TDAPIResponseFailure(
            is_successful=False,
            errors=result["errors"]
        )

        return make_response(jsonify(api_response), 422)

    data: TDBanData = result['data']
    banned_artist = ban_artist(data['id'], data['service'])
    api_response = TDAPIResponseSuccess(
        is_successful=True,
        data=banned_artist
    )

    return make_response(jsonify(api_response), 200)


@administrator_api.delete("/bans")
def artist_unban():
    result = validate_ban_api_request(request)

    if (not result['is_successful']):
        api_response = TDAPIResponseFailure(
            is_successful=False,
            errors=result['errors']
        )

        return make_response(jsonify(api_response), 422)

    data: TDBanData = result['data']
    unbanned_artist = unban_artist(data['id'], data['service'])
    api_response = TDAPIResponseSuccess(
        is_successful=True,
        data=unbanned_artist
    )

    return make_response(jsonify(api_response), 200)
