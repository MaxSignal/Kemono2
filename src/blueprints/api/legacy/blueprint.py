from typing import List

from flask import Blueprint, jsonify, make_response, redirect, request, url_for

from src.blueprints.api.v1.types import TDArtist
from src.internals.database.database import get_cursor

legacy_api = Blueprint('legacy_api', __name__)


@legacy_api.get('/favorites')
def api_list():
    new_url = url_for('api.v1.account.list_account_favorites', **request.args)
    return redirect(new_url, 301)


# @TODO: deprecate once server name search is in place
@legacy_api.route('/creators')
def creators():
    # new_url = url_for('api.v1.list_artists', **request.args)
    # return redirect(new_url, 301)
    cursor = get_cursor()
    query = """
        SELECT id, indexed, name, service, updated
        FROM lookup
            WHERE service != 'discord-channel'
        ORDER BY
            indexed ASC,
            name ASC,
            service ASC
    """
    cursor.execute(query)
    artists: List[TDArtist] = cursor.fetchall()

    return make_response(jsonify(artists), 200)


@legacy_api.get('/bans')
def bans():
    new_url = url_for('api.v1.list_banned_artists', **request.args)

    return redirect(new_url, 301)
