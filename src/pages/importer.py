import json
from datetime import datetime
from os import getenv

from flask import (Blueprint, current_app, g, make_response, render_template,
                   request, session)

from src.internals.cache.redis import (deserialize_dict_list, get_conn,
                                       scan_keys, serialize_dict_list)
from src.lib.dms import approve_dm, cleanup_unapproved_dms, get_unapproved_dms
from src.types.kemono import Unapproved_DM
from src.types.props import SuccessProps
from src.utils.utils import get_import_id

from .importer_types import DMPageProps, ImportProps, StatusPageProps

importer_page = Blueprint('importer_page', __name__)


@importer_page.get('/importer')
def importer():
    props = ImportProps()

    response = make_response(render_template(
        'importer_list.html',
        props = props
    ), 200)
    response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
    return response


@importer_page.get('/importer/tutorial')
def importer_tutorial():
    props = ImportProps()

    response = make_response(render_template(
        'importer_tutorial.html',
        props = props
    ), 200)
    response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
    return response


@importer_page.get('/importer/ok')
def importer_ok():
    props = ImportProps()

    response = make_response(render_template(
        'importer_ok.html',
        props = props
    ), 200)
    response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
    return response


@importer_page.get('/importer/status/<import_id>')
def importer_status(import_id):
    is_dms = bool(request.args.get('dms'))

    props = StatusPageProps(
        import_id=import_id,
        is_dms=is_dms
    )
    response = make_response(render_template(
        'importer_status.html',
        props = props
    ), 200)

    response.headers['Cache-Control'] = 'max-age=0, private, must-revalidate'
    return response


@importer_page.get('/importer/dms/<import_id>')
def importer_dms(import_id: str):
    account_id: str = session.get('account_id')
    dms = get_unapproved_dms(import_id, account_id) if account_id else []

    props = DMPageProps(
        import_id=import_id,
        account_id=account_id,
        dms=dms
    )

    response = make_response(render_template(
        'importer/dms.html',
        props=props,
    ), 200)

    response.headers['Cache-Control'] = 'max-age=0, private, must-revalidate'
    return response


@importer_page.post('/importer/dms/<import_id>')
def approve_importer_dms(import_id):
    props = SuccessProps(
        currentPage="import",
        redirect=f'/importer/status/{import_id}'
    )
    SuccessProps
    approved_ids = request.form.getlist('approved_ids')
    for dm_id in approved_ids:
        approve_dm(import_id, dm_id)
    cleanup_unapproved_dms(import_id)

    response = make_response(render_template(
        'success.html',
        props = props
    ), 200)

    response.headers['Cache-Control'] = 'max-age=0, private, must-revalidate'
    return response

@importer_page.route('/api/logs/<import_id>')
def get_importer_logs(import_id: str):
    redis = get_conn()
    key = f'importer_logs:{import_id}'
    llen = redis.llen(key)
    messages = []
    if llen > 0:
        messages = redis.lrange(key, 0, llen)
        redis.expire(key, 60 * 60 * 48)

    return json.dumps(list(map(lambda msg: msg.decode('utf-8'), messages))), 200

### API ###
@importer_page.route('/api/import', methods=['POST'])
def importer_submit():
    if not session.get('account_id') and request.form.get("save_dms"):
        return 'You must be logged in to import direct messages.', 401
    
    if not request.form.get("session_key"):
        return "Session key missing.", 401
    
    if request.form.get('session_key') and len(request.form.get('session_key').encode('utf-8')) > 1024:
        return "The length of the session key you sent is too large. You should let the administrator know about this.", 400
    
    if request.form.get("service") not in g.paysite_list:
        return "Service unsupported.", 400
    
    try:
        redis = get_conn()

        for _import in scan_keys('imports:*'):
            _import = _import.decode('utf8')
            existing_import = redis.get(_import)
            existing_import_data = json.loads(existing_import)
            if existing_import_data['key'] == request.form.get("session_key"):
                props = {
                    'message': 'This key is already being used for an import. Redirecting to logs...',
                    'currentPage': 'import',
                    'redirect': f"/importer/status/{_import.split(':')[1]}{ '?dms=1' if request.form.get('save_dms') else '' }"
                }

                return make_response(render_template(
                    'success.html',
                    props=props
                ), 200)

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
        redis.set(f'imports:{import_id}', json.dumps(data))

        msg = 'Successfully added your import to the queue. Waiting...'
        msg = f'[{import_id}]@{datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}: {msg}'
        redis.rpush(f'importer_logs:{import_id}', msg)

        props = {
            'currentPage': 'import',
            'redirect': f'/importer/status/{import_id}{ "?dms=1" if request.form.get("save_dms") else "" }'
        }

        return make_response(render_template(
            'success.html',
            props=props
        ), 200)
    except Exception as e:
        current_app.logger.exception('Error connecting to archiver')
        return f'Error while pushing import request. Is Redis running?', 500
