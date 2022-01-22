from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from flask import Blueprint, make_response, render_template, request

from src.internals.types import PageProps
from src.lib.artist import get_artist
from src.lib.dms import (get_all_dms, get_all_dms_by_query,
                         get_all_dms_by_query_count, get_all_dms_count)
from src.utils.utils import limit_int, parse_int
from src.types.kemono import Approved_DM


@dataclass
class DMsProps(PageProps):
    currentPage = 'artists'
    count: int
    limit: int
    dms: List[Approved_DM]
    artists: List[Dict]


dms = Blueprint('dms', __name__)


@dms.route('/dms')
def get_dms():
    base = request.args.to_dict()
    base.pop('o', None)

    offset = parse_int(request.args.get('o'), 0)  # noqa F811
    query = request.args.get('q')
    limit = limit_int(int(request.args.get('limit') or 25), 50)
    dms = None
    total_count = None

    if query is None:
        (dms, total_count) = get_dm_page(offset, limit)
    else:
        (dms, total_count) = do_dm_search(query, offset, limit)

    artists = [get_artist(dm.service, dm.user) for dm in dms]

    props = DMsProps(
        count=total_count,
        limit=limit,
        dms=dms,
        artists=artists
    )

    response = make_response(render_template(
        'all_dms.html',
        props=props,
        base=base,
    ), 200)
    response.headers['Cache-Control'] = 's-maxage=60'
    return response


def get_dm_page(offset: int, limit: int):  # noqa F811
    # @REVIEW: TypeError: dict is not a sequence
    # @RESPONSE: can't debug db queries until the test importer is fixed
    # @RESPONSE: done
    posts = get_all_dms(offset, limit)
    total_count = get_all_dms_count()
    return (posts, total_count)


def do_dm_search(q: str, offset: int, limit: int):  # noqa F811
    posts = get_all_dms_by_query(q, offset, limit)
    total_count = get_all_dms_by_query_count(q)
    return (posts, total_count)
