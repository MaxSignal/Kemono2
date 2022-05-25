from flask import Blueprint, request, redirect, url_for

legacy_api = Blueprint('legacy_api', __name__)


@legacy_api.get('/favorites')
def api_list():
    new_url = url_for('api.v1.list_account_favorites', **request.args)
    return redirect(new_url, 301)
