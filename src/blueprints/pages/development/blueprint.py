import requests
from os import getenv
from flask import (
    g,
    Blueprint,
    current_app,
    make_response,
    redirect,
    render_template,
    request,
    url_for
)

from .test_entries import test_entries

development = Blueprint('development', __name__, url_prefix="/development")


@development.before_request
def check_creds():
    if not g.get('account'):
        return redirect(url_for('account.get_login'))


@development.get('/')
def home_page():
    props = dict(
        currentPage='development'
    )

    response = make_response(render_template(
        'development/home.html',
        props=props
    ), 200)
    return response


development.register_blueprint(test_entries)
