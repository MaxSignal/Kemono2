import requests
from flask import Blueprint, g, redirect, url_for, make_response, render_template, current_app

from configs.derived_vars import archiver_origin
from src.types.account import Account
from src.types.props import SuccessProps

test_entries = Blueprint('test_entries', __name__)


@test_entries.get('/test-entries')
def test_entries_page():
    props = dict(
        currentPage='development'
    )

    response = make_response(render_template(
        'development/test_entries.html',
        props=props
    ), 200)
    return response


@test_entries.post('/test-entries/seeded')
def generate_seeded_db():
    account: Account = g.account
    try:
        response = requests.post(
            f'{archiver_origin}/development/test-entries/seeded',
            data=dict(
                account_id=str(account.id)
            )
        )

        response.raise_for_status()
        import_id = response.text
        props = SuccessProps(
            currentPage='development',
            redirect=f'/importer/status/{import_id}?dms=1'
        )

        return make_response(render_template(
            'success.html',
            props=props
        ), 200)
    except Exception:
        current_app.logger.exception('Error connecting to archver')
        return 'Error while connecting to archiver. Is it running?', 500


@test_entries.post('/test-entries/random')
def generate_random_db():
    account: Account = g.account
    try:
        response = requests.post(
            f'{archiver_origin}/development/test-entries/random',
            data=dict(
                account_id=str(account.id)
            )
        )

        response.raise_for_status()
        import_id = response.text
        props = SuccessProps(
            currentPage='development',
            redirect=f'/importer/status/{import_id}?dms=1'
        )

        return make_response(render_template(
            'success.html',
            props=props
        ), 200)
    except Exception:
        current_app.logger.exception('Error connecting to archiver')
        return 'Error while connecting to archiver. Is it running?', 500
