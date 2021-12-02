# import urllib
import json

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from configs.env_vars import DERIVED_VARS
from src.lib.account import (
    attempt_login,
    create_account,
    get_saved_key_import_ids,
    get_saved_keys,
    is_username_taken,
    load_account,
    revoke_saved_keys
)
from src.lib.notification import (
    count_account_notifications,
    get_account_notifications,
    set_notifications_as_seen
)
from src.lib.security import is_password_compromised
from src.types.account import Account, Service_Key
from src.types.props import SuccessProps
from src.utils.utils import get_value, make_cache_key, set_query_parameter

# from src.internals.cache.flask_cache import cache
from .administrator import administrator
from .moderator import moderator
from .types import AccountPageProps, NotificationsProps, ServiceKeysProps

account = Blueprint('account', __name__)

# @account.before_request
# def get_account_creds():


@account.get('/account')
def get_account():
    account: Account = g.get('account')
    if not account:
        return redirect(url_for('account.get_login'))

    notifications_count = count_account_notifications(account.id)
    props = AccountPageProps(
        account=account,
        notifications_count=notifications_count
    )

    return make_response(render_template(
        'account/home.html',
        props=props
    ), 200)


@account.get('/account/notifications')
def get_notifications():
    account: Account = g.get('account')
    if not account:
        redirect(url_for('account.get_login'))

    notifications = get_account_notifications(account.id)
    props = NotificationsProps(
        notifications=notifications
    )

    seen_notif_ids = [notification.id for notification in notifications if not notification.is_seen]
    set_notifications_as_seen(seen_notif_ids)

    return make_response(render_template(
        'account/notifications.html',
        props=props
    ), 200)


@account.get('/account/keys')
def get_account_keys():
    account: Account = g.get('account')
    if not account:
        return redirect(url_for('account.get_login'))

    saved_keys = get_saved_keys(account.id)
    props = ServiceKeysProps(
        service_keys=saved_keys
    )

    saved_session_key_import_ids = []
    for key in saved_keys:
        saved_session_key_import_ids.append(get_saved_key_import_ids(key.id))

    response = make_response(render_template(
        'account/keys.html',
        props=props,
        import_ids=saved_session_key_import_ids
    ), 200)
    response.headers['Cache-Control'] = 's-maxage=60'
    return response


@account.post('/account/keys')
def revoke_service_keys():
    account: Account = g.get('account')
    if not account:
        return redirect(url_for('account.get_login'))

    keys_dict = request.form.to_dict(flat=False)
    keys_for_revocation = [int(key) for key in keys_dict['revoke']] if keys_dict.get('revoke') else []

    revoke_saved_keys(keys_for_revocation, account.id)

    props = SuccessProps(
        currentPage='account',
        redirect='/account/keys'
    )

    response = make_response(render_template(
        'success.html',
        props=props
    ), 200)
    return response


@account.get('/account/login')
def get_login():
    props = {
        'currentPage': 'login',
        'query_string': ''
    }

    account = load_account()
    if account is not None:
        return redirect(set_query_parameter(url_for('artists.list'), 'logged_in', 'yes'))

    query = request.query_string.decode('utf-8')
    if len(query) > 0:
        props['query_string'] = '?' + query

    response = make_response(render_template(
        'account/login.html',
        props=props
    ), 200)
    response.headers['Cache-Control'] = 's-maxage=60'
    return response


@account.post('/account/login')
def post_login():
    account = load_account()
    if account is not None:
        return redirect(set_query_parameter(url_for('artists.list'), 'logged_in', 'yes'))

    query = request.query_string.decode('utf-8')
    if len(query) > 0:
        query = '?' + query

    username = get_value(request.form, 'username')
    password = get_value(request.form, 'password')
    success = attempt_login(username, password)
    if not success:
        return redirect(url_for('account.get_login') + query)

    redir = get_value(request.args, 'redir')
    if redir is not None:
        return redirect(set_query_parameter(redir, 'logged_in', 'yes'))

    return redirect(set_query_parameter(url_for('artists.list'), 'logged_in', 'yes'))


@account.route('/account/logout')
def logout():
    if 'account_id' in session:
        session.pop('account_id')
    return redirect(url_for('artists.list'))


@account.get('/account/register')
def get_register():
    props = {
        'currentPage': 'login',
        'query_string': ''
    }

    account = load_account()
    if account is not None:
        return redirect(url_for('artists.list'))

    query = request.query_string.decode('utf-8')
    if len(query) > 0:
        props['query_string'] = '?' + query

    return make_response(render_template(
        'account/register.html',
        props=props
    ), 200)


@account.post('/account/register')
def post_register():
    props = {
        'query_string': ''
    }

    query = request.query_string.decode('utf-8')
    if len(query) > 0:
        props['query_string'] = '?' + query

    username = get_value(request.form, 'username')
    password = get_value(request.form, 'password')
    favorites_json = get_value(request.form, 'favorites', '[]')
    confirm_password = get_value(request.form, 'confirm_password')

    favorites = []
    if favorites_json != '':
        favorites = json.loads(favorites_json)

    errors = False
    if username.strip() == '':
        flash('Username cannot be empty')
        errors = True

    if password.strip() == '':
        flash('Password cannot be empty')
        errors = True

    if password != confirm_password:
        flash('Passwords do not match')
        errors = True

    if is_username_taken(username):
        flash('Username already taken')
        errors = True

    if DERIVED_VARS.IS_PASSWORD_VALIDATION and is_password_compromised(password):
        flash('We\'ve detected that password was compromised in a data breach on another site. Please choose a different password.')
        errors = True

    if not errors:
        success = create_account(username, password, favorites)
        if not success:
            flash('Username already taken')
            errors = True

    if not errors:
        account = attempt_login(username, password)
        if account is None:
            current_app.logger.warning("Error logging into account immediately after creation")
        flash('Account created successfully.')

        redir = get_value(request.args, 'redir')
        if redir is not None:
            return redirect(redir)

        return redirect(url_for('artists.list', logged_in='yes'))

    return make_response(render_template(
        'account/register.html',
        props=props
    ), 200)


account.register_blueprint(administrator, url_prefix='/account')
account.register_blueprint(moderator, url_prefix='/account')
