import copy
import datetime

import dateutil
import rb
import ujson

from configs.env_vars import DERIVED_VARS
from .types import nodes, KemonoRouter

cluster: rb.Cluster = None


def init():
    global cluster
    cluster = rb.Cluster(
        hosts=nodes,
        host_defaults=DERIVED_VARS.REDIS_NODE_OPTIONS,
        router_cls=KemonoRouter
    )
    return cluster

# def get_pool():
#     global pool
#     return pool


def get_conn():
    return cluster.get_routing_client()


def serialize_dict(data):
    to_serialize = {
        'dates': [],
        'data': {}
    }

    for key, value in data.items():
        if type(value) is datetime.datetime:
            to_serialize['dates'].append(key)
            to_serialize['data'][key] = value.isoformat()
        else:
            to_serialize['data'][key] = value

    return ujson.dumps(to_serialize)


def deserialize_dict(data):
    data = ujson.loads(data)
    to_return = {}
    for key, value in data['data'].items():
        if key in data['dates']:
            to_return[key] = dateutil.parser.parse(value)
        else:
            to_return[key] = value
    return to_return


def serialize_dict_list(data):
    data = copy.deepcopy(data)
    return ujson.dumps(list(map(lambda elem: serialize_dict(elem), data)))


def deserialize_dict_list(data):
    data = ujson.loads(data)
    to_return = list(map(lambda elem: deserialize_dict(elem), data))
    return to_return
