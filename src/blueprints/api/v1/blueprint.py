import math

from flask import Blueprint, jsonify, make_response, redirect, request, url_for

from src.lib.account import load_account
from src.lib.favorites import get_favorite_artists, get_favorite_posts
from src.utils.utils import get_value, parse_int

from .lib import count_artists, get_artists, validate_artists_request
from .types import (
    DEFAULT_PAGE_LIMIT,
    TDAPIResponseFaillure,
    TDAPIResponseSuccess,
    TDArtistResponse,
    TDArtistsParams,
    TDPagination,
    TDPaginationDB,
    TDPaginationInit
)

v1api = Blueprint('v1', __name__, url_prefix='/v1')


@v1api.get("/account/favorites")
def list_account_favorites():
    account = load_account()
    if account is None:
        return {}, 401

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


@v1api.get("/artists")
def get_artists_last():
    """
    A separate redirect page because blueprints
    cannot into path with undefined parameters.
    """
    limit = DEFAULT_PAGE_LIMIT
    artist_count = count_artists()
    total_pages = math.floor(artist_count / limit) + 1
    redirect_url = url_for('.list_artists', page=total_pages, **request.args)

    return redirect(redirect_url, 302)


@v1api.get("/artists/<page>")
def list_artists(page: str):
    result = validate_artists_request(request)

    if not result["is_successful"]:
        api_response = TDAPIResponseFaillure(
            is_successful=False,
            errors=result["errors"]
        )
        response = make_response(jsonify(api_response), 422)
        return response

    search_params: TDArtistsParams = result['data']
    service = search_params["service"]
    # artist_name = search_params["name"]
    current_page = parse_int(page)
    limit = DEFAULT_PAGE_LIMIT
    artist_count = count_artists(
        service,
        # artist_name
    )
    total_pages = math.floor(artist_count / limit) + 1
    is_valid_page = current_page and current_page <= total_pages

    # current page is zero or greater than total pages
    if (not is_valid_page):
        redirect_url = url_for('.list_artists', page=total_pages, **request.args)

        return redirect(redirect_url)

    is_last_page = current_page == total_pages
    pagination_init = TDPaginationInit(
        current_page=current_page,
        limit=limit,
        total_count=artist_count,
        total_pages=total_pages
    )

    offset = (current_page - 1) * limit
    sql_limit = artist_count - offset if is_last_page else limit
    pagination_db = TDPaginationDB(
        pagination_init=pagination_init,
        offset=offset,
        sql_limit=sql_limit
    )
    artists = get_artists(
        pagination_db,
        service,
        # artist_name
    )
    pagination = TDPagination(
        total_count=artist_count,
        total_pages=total_pages,
        current_page=current_page,
        limit=limit
    )
    response_body = TDArtistResponse(
        pagination=pagination,
        artists=artists
    )
    api_response = TDAPIResponseSuccess(
        is_successful=True,
        data=response_body
    )
    response = make_response(jsonify(api_response), 200)
    response.headers['Cache-Control'] = 's-maxage=60'

    return response
