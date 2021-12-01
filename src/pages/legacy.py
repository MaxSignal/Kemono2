import json
import random
import string
from datetime import datetime
from hashlib import sha256
from os import makedirs, stat
from os.path import basename, join

import requests
from bleach.sanitizer import Cleaner
from flask import (
    Blueprint,
    abort,
    jsonify,
    make_response,
    render_template,
    render_template_string,
    request,
)
from python_resumable import UploaderFlask
from slugify import slugify_filename
from werkzeug.utils import secure_filename

from configs.env_vars import ENV_VARS
from src.internals.cache.flask_cache import cache
from src.internals.database.database import get_cursor
from src.utils.utils import (
    allowed_file,
    make_cache_key,
)

legacy = Blueprint('legacy', __name__)


@legacy.route('/posts/upload')
def upload_post():
    props = {
        'currentPage': 'posts'
    }
    response = make_response(render_template(
        'upload.html',
        props=props
    ), 200)
    response.headers['Cache-Control'] = 's-maxage=60'
    return response


@legacy.route('/discord/server/<id>')
def discord_server(id):
    response = make_response(render_template(
        'discord.html'
    ), 200)
    response.headers['Cache-Control'] = 's-maxage=60'
    return response


@legacy.route('/board')
def board():
    props = {
        'currentPage': 'board'
    }
    response = make_response(render_template(
        'board_list.html',
        props=props
    ), 200)
    response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
    return response


@legacy.route('/requests')
def requests_list():
    props = {
        'currentPage': 'requests'
    }
    base = request.args.to_dict()
    base.pop('o', None)
    props['limit'] = 25

    if not request.args.get('commit'):
        query = "SELECT * FROM requests "
        query += "WHERE status = 'open' "
        query += "ORDER BY votes desc "
        query += "OFFSET %s "
        offset = request.args.get('o') if request.args.get('o') else 0
        params = (offset,)
        query += "LIMIT 25"

        cursor2 = get_cursor()
        query2 = "SELECT COUNT(*) FROM requests "
        query2 += "WHERE status = 'open'"
        cursor2.execute(query2)
        results2 = cursor2.fetchall()
        props["count"] = int(results2[0]["count"])
    else:
        query = "SELECT * FROM requests "
        query += "WHERE title ILIKE %s "
        params = ('%' + request.args.get('q') + '%',)
        if request.args.get('service'):
            query += "AND service = %s "
            params += (request.args.get('service'),)
        query += "AND service != 'discord' "
        if request.args.get('max_price'):
            query += "AND price <= %s "
            params += (request.args.get('max_price'),)
        query += "AND status = %s "
        params += (request.args.get('status'),)
        query += "ORDER BY " + {
            'votes': 'votes',
            'created': 'created',
            'price': 'price'
        }.get(request.args.get('sort_by'), 'votes')
        query += {
            'asc': ' asc ',
            'desc': ' desc '
        }.get(request.args.get('order'), 'desc')
        query += "OFFSET %s "
        offset = request.args.get('o') if request.args.get('o') else 0
        params += (offset,)
        query += "LIMIT 25"

        cursor2 = get_cursor()
        query2 = "SELECT COUNT(*) FROM requests "
        query2 += "WHERE title ILIKE %s "
        params2 = ('%' + request.args.get('q') + '%',)
        if request.args.get('service'):
            query2 += "AND service = %s "
            params2 += (request.args.get('service'),)
        query2 += "AND service != 'discord' "
        if request.args.get('max_price'):
            query2 += "AND price <= %s "
            params2 += (request.args.get('max_price'),)
        query2 += "AND status = %s"
        params2 += (request.args.get('status'),)
        cursor2.execute(query2, params2)
        results2 = cursor2.fetchall()
        props["count"] = int(results2[0]["count"])

    cursor = get_cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()

    response = make_response(render_template(
        'requests_list.html',
        props=props,
        results=results,
        base=base
    ), 200)
    return response


@legacy.route('/requests/<id>/vote_up', methods=['POST'])
def vote_up(id):
    ip = request.headers.getlist(
        "X-Forwarded-For")[0].rpartition(' ')[-1] if 'X-Forwarded-For' in request.headers else request.remote_addr
    query = "SELECT * FROM requests WHERE id = %s"
    params = (id,)

    cursor = get_cursor()
    cursor.execute(query, params)
    result = cursor.fetchone()

    props = {
        'currentPage': 'requests',
        'redirect': request.args.get('Referer') if request.args.get('Referer') else '/requests'
    }

    if not len(result):
        abort(404)
    hash = sha256(ip.encode()).hexdigest()
    if hash in result.get('ips'):
        props['message'] = 'You already voted on this request.'
        return make_response(render_template(
            'error.html',
            props=props
        ), 401)
    else:
        record = result.get('ips')
        record.append(hash)
        query = "UPDATE requests SET votes = votes + 1,"
        query += "ips = %s "
        params = (record,)
        query += "WHERE id = %s"
        params += (id,)
        cursor.execute(query, params)

        return make_response(render_template(
            'success.html',
            props=props
        ), 200)


@legacy.route('/requests/new')
def request_form():
    props = {
        'currentPage': 'requests'
    }

    response = make_response(render_template(
        'requests_new.html',
        props=props
    ), 200)
    response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
    return response


@legacy.route('/requests/new', methods=['POST'])
def request_submit():
    props = {
        'currentPage': 'requests',
        'redirect': request.args.get('Referer') if request.args.get('Referer') else '/requests'
    }

    ip = request.headers.getlist(
        "X-Forwarded-For")[0].rpartition(' ')[-1] if 'X-Forwarded-For' in request.headers else request.remote_addr

    if not request.form.get('user_id'):
        props['message'] = 'You didn\'t enter a user ID.'
        return make_response(render_template(
            'error.html',
            props=props
        ), 400)

    if ENV_VARS.TELEGRAMTOKEN:
        snippet = ''
        with open('views/requests_new.html', 'r') as file:
            snippet = file.read()

        requests.post(
            f'https://api.telegram.org/bot{ENV_VARS.TELEGRAMTOKEN}/sendMessage',
            params={
                'chat_id': f'-{ENV_VARS.TELEGRAMCHANNEL}',
                'parse_mode': 'HTML',
                'text': render_template_string(snippet)
            }
        )

    filename = ''
    try:
        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename and allowed_file(image.content_type, ['png', 'jpeg', 'gif']):
                filename = slugify_filename(secure_filename(image.filename))
                tmp = join('/tmp', filename)
                image.save(tmp)
                limit = int(ENV_VARS.REQUEST_IMAGES)
                if stat(tmp).st_size > limit:
                    abort(413)
                try:
                    host = ENV_VARS.ARCHIVER_HOST
                    port = ENV_VARS.ARCHIVER_PORT
                    r = requests.post(
                        f'http://{host}:{port}/api/upload/requests/images',
                        files={'file': open(tmp, 'rb')}
                    )
                    filename = basename(r.text)
                    r.raise_for_status()
                except Exception:
                    return 'Error while connecting to archiver.', 500
    except Exception as error:
        props['message'] = 'Failed to upload image. Error: {}'.format(error)
        return make_response(render_template(
            'error.html',
            props=props
        ), 500)

    scrub = Cleaner(tags=[])
    text = Cleaner(tags=['br'])

    columns = ['service', '"user"', 'title', 'description', 'price', 'ips']
    description = request.form.get('description').strip().replace('\n', '<br>\n')
    params = (
        scrub.clean(request.form.get('service')),
        scrub.clean(request.form.get('user_id').strip()),
        scrub.clean(request.form.get('title').strip()),
        text.clean(description),
        scrub.clean(request.form.get('price').strip()),
        [sha256(ip.encode()).hexdigest()]
    )
    if request.form.get('specific_id'):
        columns.append('post_id')
        params += (scrub.clean(request.form.get('specific_id').strip()),)
    if filename:
        columns.append('image')
        params += (join('/requests', 'images', filename),)
    data = ['%s'] * len(params)

    query = "INSERT INTO requests ({fields}) VALUES ({values})".format(
        fields=','.join(columns),
        values=','.join(data)
    )

    cursor = get_cursor()
    cursor.execute(query, params)

    return make_response(render_template(
        'success.html',
        props=props
    ), 200)


@legacy.route('/api/upload', methods=['POST'])
def upload():
    resumable_dict = {
        'resumableIdentifier': request.form.get('resumableIdentifier'),
        'resumableFilename': request.form.get('resumableFilename'),
        'resumableTotalSize': request.form.get('resumableTotalSize'),
        'resumableTotalChunks': request.form.get('resumableTotalChunks'),
        'resumableChunkNumber': request.form.get('resumableChunkNumber')
    }

    if int(request.form.get('resumableTotalSize')) > int(ENV_VARS.UPLOAD_LIMIT):
        return ("File too large.", 415)

    makedirs('/tmp/uploads', exist_ok=True)
    makedirs('/tmp/uploads/incomplete', exist_ok=True)

    resumable = UploaderFlask(
        resumable_dict,
        '/tmp/uploads',
        '/tmp/uploads/incomplete',
        request.files['file']
    )

    resumable.upload_chunk()

    if resumable.check_status() is True:
        resumable.assemble_chunks()
        try:
            resumable.cleanup()
        except:
            pass

        try:
            host = ENV_VARS.ARCHIVER_HOST
            port = ENV_VARS.ARCHIVER_PORT
            r = requests.post(
                f'http://{host}:{port}/api/upload/uploads',
                files={'file': open(join('/tmp/uploads', request.form.get('resumableFilename')), 'rb')}
            )
            final_path = r.text
            r.raise_for_status()
        except Exception:
            return 'Error while connecting to archiver.', 500

        post_model = {
            'id': ''.join(random.choice(string.ascii_letters) for x in range(8)),
            '"user"': request.form.get('user'),
            'service': request.form.get('service'),
            'title': request.form.get('title'),
            'content': request.form.get('content') or "",
            'embed': {},
            'shared_file': True,
            'added': datetime.now(),
            'published': datetime.now(),
            'edited': None,
            'file': {
                "name": basename(final_path),
                "path": final_path
            },
            'attachments': []
        }

        post_model['embed'] = json.dumps(post_model['embed'])
        post_model['file'] = json.dumps(post_model['file'])

        columns = post_model.keys()
        data = ['%s'] * len(post_model.values())
        data[-1] = '%s::jsonb[]'  # attachments
        query = "INSERT INTO posts ({fields}) VALUES ({values})".format(
            fields=','.join(columns),
            values=','.join(data)
        )
        cursor = get_cursor()
        cursor.execute(query, list(post_model.values()))

        return jsonify({
            "fileUploadStatus": True,
            "resumableIdentifier": resumable.repo.file_id
        })

    return jsonify({
        "chunkUploadStatus": True,
        "resumableIdentifier": resumable.repo.file_id
    })


@legacy.route('/api/creators')
def creators():
    cursor = get_cursor()
    query = "SELECT * FROM lookup WHERE service != 'discord-channel'"
    cursor.execute(query)
    results = cursor.fetchall()
    return make_response(jsonify(results), 200)


@legacy.route('/api/bans')
def bans():
    cursor = get_cursor()
    query = "SELECT * FROM dnp"
    cursor.execute(query)
    results = cursor.fetchall()
    return make_response(jsonify(results), 200)


@legacy.route('/api/recent')
def recent():
    cursor = get_cursor()
    query = "SELECT * FROM posts ORDER BY added desc "
    params = ()

    offset = request.args.get('o') if request.args.get('o') else 0
    query += "OFFSET %s "
    params += (offset,)
    limit = request.args.get('limit') if request.args.get('limit') and int(request.args.get('limit')) <= 50 else 25
    query += "LIMIT %s"
    params += (limit,)

    cursor.execute(query, params)
    results = cursor.fetchall()

    response = make_response(jsonify(results), 200)
    response.headers['Cache-Control'] = 'max-age=60, public, stale-while-revalidate=2592000'
    return response


@legacy.route('/api/lookup')
def lookup():
    if (request.args.get('q') is None):
        return make_response('Bad request', 400)
    cursor = get_cursor()
    query = "SELECT * FROM lookup "
    params = ()
    query += "WHERE name ILIKE %s "
    params += ('%' + request.args.get('q') + '%',)
    if (request.args.get('service')):
        query += "AND service = %s "
        params += (request.args.get('service'),)
    limit = request.args.get('limit') if request.args.get('limit') and int(request.args.get('limit')) <= 150 else 50
    query += "LIMIT %s"
    params += (limit,)

    cursor.execute(query, params)
    results = cursor.fetchall()
    response = make_response(jsonify(list(map(lambda x: x['id'], results))), 200)
    return response


@legacy.route('/api/discord/channels/lookup')
def discord_lookup():
    cursor = get_cursor()
    query = "SELECT channel FROM discord_posts WHERE server = %s GROUP BY channel"
    params = (request.args.get('q'),)
    cursor.execute(query, params)
    channels = cursor.fetchall()
    lookup = []
    for x in channels:
        cursor = get_cursor()
        cursor.execute("SELECT * FROM lookup WHERE service = 'discord-channel' AND id = %s", (x['channel'],))
        lookup_result = cursor.fetchall()
        lookup.append({'id': x['channel'], 'name': lookup_result[0]['name'] if len(lookup_result) else ''})
    response = make_response(jsonify(lookup))
    return response


@legacy.route('/api/discord/channel/<id>')
def discord_channel(id):
    cursor = get_cursor()
    query = "SELECT * FROM discord_posts WHERE channel = %s ORDER BY published desc "
    params = (id,)

    offset = request.args.get('skip') if request.args.get('skip') else 0
    query += "OFFSET %s "
    params += (offset,)
    limit = request.args.get('limit') if request.args.get('limit') and int(request.args.get('limit')) <= 150 else 25
    query += "LIMIT %s"
    params += (limit,)

    cursor.execute(query, params)
    results = cursor.fetchall()
    return jsonify(results)


@legacy.route('/api/lookup/cache/<id>')
def lookup_cache(id):
    if (request.args.get('service') is None):
        return make_response('Bad request', 400)
    cursor = get_cursor()
    query = "SELECT * FROM lookup WHERE id = %s AND service = %s"
    params = (id, request.args.get('service'))
    cursor.execute(query, params)
    results = cursor.fetchall()
    response = make_response(jsonify({"name": results[0]['name'] if len(results) > 0 else ''}))
    return response


@legacy.route('/api/<service>/user/<user>/lookup')
def user_search(service, user):
    if (request.args.get('q') and len(request.args.get('q')) > 35):
        return make_response('Bad request', 400)
    cursor = get_cursor()
    query = "SELECT * FROM posts WHERE \"user\" = %s AND service = %s "
    params = (user, service)
    query += "AND to_tsvector(content || ' ' || title) @@ websearch_to_tsquery(%s) "
    params += (request.args.get('q'),)
    query += "ORDER BY published desc "

    offset = request.args.get('o') if request.args.get('o') else 0
    query += "OFFSET %s "
    params += (offset,)
    limit = request.args.get('limit') if request.args.get('limit') and int(request.args.get('limit')) <= 150 else 25
    query += "LIMIT %s"
    params += (limit,)

    cursor.execute(query, params)
    results = cursor.fetchall()
    return jsonify(results)


@legacy.route('/api/<service>/user/<user>/post/<post>')
def post_api(service, user, post):
    cursor = get_cursor()
    query = "SELECT * FROM posts WHERE id = %s AND \"user\" = %s AND service = %s ORDER BY added asc"
    params = (post, user, service)
    cursor.execute(query, params)
    results = cursor.fetchall()
    return jsonify(results)


@legacy.route('/api/<service>/user/<user>/post/<post>/flag')
def flag_api(service, user, post):
    cursor = get_cursor()
    query = "SELECT * FROM booru_flags WHERE id = %s AND \"user\" = %s AND service = %s"
    params = (post, user, service)
    cursor.execute(query, params)
    results = cursor.fetchall()
    return "", 200 if len(results) else 404


@legacy.route('/api/<service>/user/<user>/post/<post>/flag', methods=["POST"])
def new_flag_api(service, user, post):
    cursor = get_cursor()
    query = "SELECT * FROM posts WHERE id = %s AND \"user\" = %s AND service = %s"
    params = (post, user, service)
    cursor.execute(query, params)
    results = cursor.fetchall()
    if len(results) == 0:
        return "", 404

    cursor2 = get_cursor()
    query2 = "SELECT * FROM booru_flags WHERE id = %s AND \"user\" = %s AND service = %s"
    params2 = (post, user, service)
    cursor2.execute(query2, params2)
    results2 = cursor.fetchall()
    if len(results2) > 0:
        # conflict; flag already exists
        return "", 409

    scrub = Cleaner(tags=[])
    columns = ['id', '"user"', 'service']
    params = (
        scrub.clean(post),
        scrub.clean(user),
        scrub.clean(service)
    )
    data = ['%s'] * len(params)
    query = "INSERT INTO booru_flags ({fields}) VALUES ({values})".format(
        fields=','.join(columns),
        values=','.join(data)
    )
    cursor3 = get_cursor()
    cursor3.execute(query, params)

    return "", 200


@legacy.route('/api/<service>/user/<id>')
@cache.cached(key_prefix=make_cache_key)
def user_api(service, id):
    cursor = get_cursor()
    query = "SELECT * FROM posts WHERE \"user\" = %s AND service = %s ORDER BY published desc "
    params = (id, service)

    offset = request.args.get('o') if request.args.get('o') else 0
    query += "OFFSET %s "
    params += (offset,)
    limit = request.args.get('limit') if request.args.get('limit') and int(request.args.get('limit')) <= 50 else 25
    query += "LIMIT %s"
    params += (limit,)

    cursor.execute(query, params)
    results = cursor.fetchall()

    return jsonify(results)
