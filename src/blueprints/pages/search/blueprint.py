import requests
from os import getenv
from flask import (
    Blueprint,
    current_app,
    make_response,
    redirect,
    render_template,
    request,
    url_for
)

search = Blueprint('pages', __name__, url_prefix='/search')


@search.get("/")
def search_page():
    """
    For the time being redirect to artist search.
    """
    redirect_url = url_for(".search_artists_page", **request.args)
    return redirect(redirect_url, 302)


@search.get("/artists")
def search_artists_page():
    props = dict()
    response = make_response(render_template(
        'search/artists.html',
        props=props
    ), 200)
    response.headers['Cache-Control'] = 's-maxage=60'

    return response
