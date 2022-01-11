import requests
from flask import (
    Blueprint,
    current_app,
    make_response,
    redirect,
    render_template,
    request
)

pages = Blueprint('api', __name__)


@pages.get('/')
def get_home():
    props = {}
    base = request.args.to_dict()
    base.pop('o', None)
    response = make_response(render_template(
        'home.html',
        props=props,
        base=base
    ), 200)
    response.headers['Cache-Control'] = 's-maxage=60'
    return response


@pages.get('/antiscraper')
def do_antiscraper_thing():
    """
    Pass the url param to the proxy server.
    """
    params = request.args.to_dict()
    url = params['antiscraper-url']
    try:
        res = requests.get(
            url,
            proxies={
                'http': 'http://10.0.0.1:3128',
                'https': 'http://10.0.0.1:3128'
            },
            headers={
                'referer': "https://www.patreon.com"
            },
        )
        res.raise_for_status()
        return redirect(res.url)
    except requests.HTTPError as error:
        current_app.logger.exception(f'Couldn\'t bypass "{url}". Reason: {error}')
    except Exception as error:
        current_app.logger.exception(f'Couldn\'t bypass "{url}". Reason: {error}')
        return ('Error while trying to bypass the antiscraper link. The admins were notified of the problem.', 500)
