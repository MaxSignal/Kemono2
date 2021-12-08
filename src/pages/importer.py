import json
from src.internals.cache.redis import get_conn, serialize_dict_list, deserialize_dict_list
from src.utils.utils import get_import_id
from flask import Blueprint, request, make_response, render_template, current_app, g, session
from base64 import b64encode
from src.lib.dms import get_unapproved_dms, approve_dm, cleanup_unapproved_dms

from src.types.props import SuccessProps
from .importer_types import DMPageProps, StatusPageProps

importer_page = Blueprint('importer_page', __name__)


@importer_page.route('/importer')
def importer():
    props = {
        'currentPage': 'import'
    }

    response = make_response(render_template(
        'importer_list.html',
        props=props
    ), 200)
    response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
    return response


@importer_page.route('/importer/tutorial')
def importer_tutorial():
    props = {
        'currentPage': 'import'
    }

    response = make_response(render_template(
        'importer_tutorial.html',
        props=props
    ), 200)
    response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
    return response


@importer_page.route('/importer/ok')
def importer_ok():
    props = {
        'currentPage': 'import'
    }

    response = make_response(render_template(
        'importer_ok.html',
        props=props
    ), 200)
    response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
    return response


@importer_page.route('/importer/status/<import_id>')
def importer_status(import_id):
    dms = request.args.get('dms')

    props = StatusPageProps(
        currentPage='import',
        import_id=import_id,
        dms=dms
    )
    response = make_response(render_template(
        'importer_status.html',
        props=props
    ), 200)

    response.headers['Cache-Control'] = 'max-age=0, private, must-revalidate'
    return response


@importer_page.route('/importer/dms/<import_id>', methods=['GET'])
def importer_dms(import_id: str):
    account_id = session.get('account_id')
    dms = get_unapproved_dms(import_id)
    filtered_dms = []
    for dm in dms:
        if dm.contributor_id == str(account_id):
            filtered_dms.append(dm)

    props = DMPageProps(
        currentPage='import',
        import_id=import_id,
        account_id=account_id,
        dms=filtered_dms
    )

    response = make_response(render_template(
        'importer_dms.html',
        props=props,
    ), 200)

    response.headers['Cache-Control'] = 'max-age=0, private, must-revalidate'
    return response


@importer_page.route('/importer/dms/<import_id>', methods=['POST'])
def approve_importer_dms(import_id):
    props = {
        'currentPage': 'import',
        'redirect': f'/importer/status/{import_id}'
    }

    approved_ids = request.form.getlist('approved_ids')
    for dm_id in approved_ids:
        approve_dm(import_id, dm_id)
    cleanup_unapproved_dms(import_id)

    response = make_response(render_template(
        'success.html',
        props=props
    ), 200)

    response.headers['Cache-Control'] = 'max-age=0, private, must-revalidate'
    return response


@importer_page.route('/api/logs/<import_id>')
def get_importer_logs(import_id):
    redis = get_conn()
    key = f'importer_logs:{import_id}'
    llen = redis.llen(key)
    messages = []
    if llen > 0:
        messages = redis.lrange(key, 0, llen)
        redis.expire(key, 60 * 60 * 48)

    return json.dumps(list(map(lambda msg: msg.decode('utf-8'), messages))), 200


# API
@importer_page.post('/api/import')
def importer_submit():
    session_key = request.form.get("session_key")

    if not session.get('account_id') and request.form.get("save_dms"):
        return 'You must be logged in to import direct messages.', 401

    if not session_key:
        return "Session key missing.", 401

    if request.form.get("service") not in g.paysite_list:
        return "Service unsupported.", 400

    if request.form.get("service") == 'onlyfans':
        session_key = b64encode(json.dumps({
            'sess': request.form.get("session_key"),
            'auth_id': request.form.get("auth_id"),
            'auth_uid_': None,  # TODO: support 2fa accounts
            'x-bc': request.form.get("x-bc"),
            'user_agent': request.form.get("user_agent")
        }).encode('utf-8')).decode()

    try:
        redis = get_conn()
        import_id = get_import_id(request.form.get("session_key"))
        data = dict(
            key=session_key,
            service=request.form.get("service"),
            channel_ids=request.form.get("channel_ids"),
            auto_import=request.form.get("auto_import"),
            save_session_key=request.form.get("save_session_key"),
            save_dms=request.form.get("save_dms"),
            contributor_id=session.get("account_id")
        )
        redis.set('imports:' + import_id, json.dumps(data))

        props = SuccessProps(
            currentPage='import',
            redirect=f'/importer/status/{import_id}{ "?dms=1" if request.form.get("save_dms") else "" }'
        )

        return make_response(render_template(
            'success.html',
            props=props
        ), 200)
    except Exception:
        current_app.logger.exception('Error connecting to archiver')
        return 'Error while pushing import request. Is Redis running?', 500
