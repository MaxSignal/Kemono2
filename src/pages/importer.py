import json
# @REVIEW: rewrite into `import from` syntax
# @RESPONSE: done
from datetime import datetime, timezone
from src.internals.cache.redis import get_conn, serialize_dict_list, deserialize_dict_list
from src.utils.utils import get_import_id
from flask import Blueprint, request, make_response, render_template, current_app, g, session

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

    return json.dumps(list(map(lambda msg: msg.decode('utf-8'), messages))), 200


# API
@importer_page.post('/api/import')
def importer_submit():
    if not session.get('account_id') and request.form.get("save_dms"):
        return 'You must be logged in to import direct messages.', 401

    if not request.form.get("session_key"):
        return "Session key missing.", 401

    if request.form.get('session_key') and len(request.form.get('session_key').encode('utf-8')) > 1024:
        return "The length of the session key you sent is too large. You should let the administrator know about this.", 400

    try:
        redis = get_conn()
        import_id = get_import_id(request.form.get("session_key"))
        data = dict(
            key=request.form.get("session_key"),
            service=request.form.get("service"),
            channel_ids=request.form.get("channel_ids"),
            auto_import=request.form.get("auto_import"),
            save_session_key=request.form.get("save_session_key"),
            save_dms=request.form.get("save_dms"),
            contributor_id=session.get("account_id")
        )
        redis.set('imports:' + import_id, json.dumps(data))

        # @REVIEW: These are different variables and so is the timestamp.
        # Why does a random endpoint add logs to the import?
        # It's a job of the importer manager.
        # @RESPONSE: I fixed(?) the first bit, but I disagree with you on the second.
        # This message in particular needs to be sent to the user before Kitsune's watcher or importers
        # process anything, so doing it on the frontend server is the only real option.
        msg = f'[{import_id}]@{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}: '
        msg += 'Successfully added your import to the queue. Waiting...'
        redis.rpush(f'importer_logs:{import_id}', msg)

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
