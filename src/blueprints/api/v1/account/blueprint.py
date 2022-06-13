from flask import Blueprint, jsonify, make_response, request

from src.blueprints.api.v1.types import TDAPIResponseSuccess, TDAPIResponseFailure
from src.lib.account import TDAccount, load_account
from src.lib.favorites import get_favorite_artists, get_favorite_posts
from src.utils.utils import get_value, parse_int

from .administrator import administrator_api
from .types import TDAccountInfo

account_api = Blueprint('account', __name__, url_prefix='/account')


@account_api.before_request
def get_account_creds():
    if load_account():
        return

    errors = ["Not Authorized"]
    api_response = TDAPIResponseFailure(
        is_successful=False,
        errors=errors
    )

    response = make_response(jsonify(api_response), 401)

    return response


@account_api.get("/")
def get_account_details():
    account: TDAccount = load_account()
    data = TDAccountInfo(
        role=account['role']
    )
    api_response = TDAPIResponseSuccess(
        is_successful=True,
        data=data
    )
    response = make_response(jsonify(api_response), 200)

    return response


@account_api.get("/favorites")
def list_account_favorites():
    account = load_account()

    favorites = []
    fave_type = get_value(request.args, 'type', 'artist')
    if fave_type == 'post':
        favorites = get_favorite_posts(account['id'])
    else:
        favorites = get_favorite_artists(account['id'])

    results = favorites
    response = make_response(jsonify(results), 200)
    response.headers['Cache-Control'] = 's-maxage=60'
    return response


account_api.register_blueprint(administrator_api)
