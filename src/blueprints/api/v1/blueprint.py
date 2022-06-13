import math

from flask import Blueprint, jsonify, make_response, redirect, request, url_for

from src.utils.utils import parse_int

from .auth import auth_api
from .account import account_api
from .lib import (
    count_artists,
    count_banned_artists,
    get_artists,
    get_banned_artists,
    validate_artists_request
)
from .types import (
    DEFAULT_PAGE_LIMIT,
    TDAPIResponseFailure,
    TDAPIResponseSuccess,
    TDArtistResponse,
    TDArtistsParams,
    TDPagination,
    TDPaginationDB,
    TDPaginationInit
)

v1api = Blueprint('v1', __name__, url_prefix='/v1')


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
        api_response = TDAPIResponseFailure(
            is_successful=False,
            errors=result["errors"]
        )
        response = make_response(jsonify(api_response), 422)
        return response

    search_params: TDArtistsParams = result['data']
    # artist_name = search_params["name"]
    current_page = parse_int(page)
    limit = DEFAULT_PAGE_LIMIT
    artist_count = count_artists(
        search_params["service"],
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
        search_params,
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


@v1api.get('/banned-artists')
def get_banned_artists_last():
    limit = DEFAULT_PAGE_LIMIT
    artist_count = count_banned_artists()
    total_pages = math.floor(artist_count / limit) + 1
    redirect_url = url_for('.list_banned_artists', page=total_pages, **request.args)

    return redirect(redirect_url, 302)


@v1api.get('/banned-artists/<page>')
def list_banned_artists(page: str):
    total_count = count_banned_artists()
    limit = DEFAULT_PAGE_LIMIT
    current_page = parse_int(page)
    total_pages = math.floor(total_count / limit) + 1
    is_valid_page = current_page and current_page <= total_pages

    # current page is zero or greater than total pages
    if (not is_valid_page):
        redirect_url = url_for(
            '.list_banned_artists',
            page=total_pages,
            **request.args
        )

        return redirect(redirect_url)

    is_last_page = current_page == total_pages
    pagination_init = TDPaginationInit(
        current_page=current_page,
        limit=limit,
        total_count=total_count,
        total_pages=total_pages
    )
    offset = (current_page - 1) * limit
    sql_limit = total_count - offset if is_last_page else limit
    pagination_db = TDPaginationDB(
        pagination_init=pagination_init,
        offset=offset,
        sql_limit=sql_limit
    )

    banned_artists = get_banned_artists(pagination_db)

    pagination = TDPagination(
        total_count=total_count,
        total_pages=total_pages,
        current_page=current_page,
        limit=limit
    )

    response_body = TDArtistResponse(
        pagination=pagination,
        banned_artists=banned_artists
    )

    api_response = TDAPIResponseSuccess(
        is_successful=True,
        data=response_body
    )

    return make_response(jsonify(api_response), 200)


# v1api.register_blueprint(auth_api)
v1api.register_blueprint(account_api)
