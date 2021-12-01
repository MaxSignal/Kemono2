import requests
from flask import Blueprint, current_app, g, make_response, render_template

from configs.env_vars import DERIVED_VARS
from development.lib.test_accounts import (
    register_test_accounts,
    write_test_accounts_data
)
from src.types.account import Account
from src.types.props import SuccessProps

config = Blueprint('config', __name__)


@config.get('/config')
def main_page():
    props = dict(
        currentPage='development'
    )

    response = make_response(render_template(
        'development/config.html',
        props=props
    ), 200)
    return response


@config.post('/config')
def activate_dev_mode():
    accounts = register_test_accounts()
    print(f"Registered {len(accounts)} accounts.")
    write_test_accounts_data(accounts)

    props = dict(
        currentPage='development'
    )

    response = make_response(render_template(
        'success.html',
        props=props
    ), 200)
    return response


@config.get('/config/test-entries')
def test_entries():
    props = dict(
        currentPage='development'
    )

    response = make_response(render_template(
        'development/test_entries.html',
        props=props
    ), 200)
    return response


@config.post('/config/service-keys')
def generate_service_keys():
    account: Account = g.account
    try:
        req = requests.post(
            url=f"{DERIVED_VARS.ARCHIVER_ORIGIN}/development/service-keys",
            data=dict(
                account_id=str(account.id)
            )
        )
        req.raise_for_status()
        props = SuccessProps(currentPage='dev-only', redirect='/dev-only')

        response = make_response(render_template(
            'success.html',
            props=props
        ), 200)
        return response

    except Exception:
        current_app.logger.exception('Error connecting to archver')
        return 'Error while connecting to archiver. Is it running?', 500
