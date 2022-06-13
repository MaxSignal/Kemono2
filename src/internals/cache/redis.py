import copy
import datetime
from typing import List, Optional

import dateutil
import rb
import redis_lock
import ujson

import redis_map

cluster: rb.Cluster = None


class KemonoRouter(rb.BaseRouter):
    def get_host_for_key(self, key):
        top_level_prefix_of_key = key.split(':')[0]
        if (redis_map.keyspaces.get(top_level_prefix_of_key) is not None):
            return redis_map.keyspaces[top_level_prefix_of_key]
        else:
            raise rb.UnroutableCommand()


class KemonoRedisLock(redis_lock.Lock):
    def release(self):
        if self._lock_renewal_thread is not None:
            self._stop_lock_renewer()
        # soft reimplementation of UNLOCK_SCRIPT in Python
        self._client.delete(self._signal)
        self._client.lpush(self._signal, 1)
        self._client.pexpire(self._signal, self._signal_expire)
        self._client.delete(self._name)

    def extend(self, expire=None):
        if expire:
            expire = int(expire)
            if expire < 0:
                raise ValueError("A negative expire is not acceptable.")
        elif self._expire is not None:
            expire = self._expire
        else:
            raise TypeError(
                "To extend a lock 'expire' must be provided as an "
                "argument to extend() method or at initialization time."
            )
        # soft reimplementation of EXTEND_SCRIPT in Python
        self._client.expire(self._name, expire)


def init():
    global cluster
    cluster = rb.Cluster(hosts=redis_map.nodes, host_defaults=redis_map.node_options, router_cls=KemonoRouter)
    return cluster

# def get_pool():
#     global pool
#     return pool


def get_conn():
    return cluster.get_routing_client()


def scan_keys(pattern):
    return cluster.get_local_client_for_key(pattern).scan_iter(match=pattern, count=5000)


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


def serialize_dict_list(data: Optional[List]):
    data = copy.deepcopy(data) if data is not None else []
    return ujson.dumps(list(map(lambda elem: serialize_dict(elem), data)))


def deserialize_dict_list(data: str):
    data = ujson.loads(data)
    to_return = list(map(lambda elem: deserialize_dict(elem), data))
    return to_return


def create_key_constructor(namespace: str):
    """
    Creates a redis key constructor function for a given namespace.
    """
    def construct_key(*keys: str):
        """
        Filters out all falsy values in passed args
        and joins them into a redis key string.
        """
        filtered_args = (key for key in keys if key)
        key_string = ":".join((namespace, *filtered_args))
        return key_string

    return construct_key


def create_counts_key_constructor(namespace: str):
    """
    Creates a `counts:` redis key constructor function for a given namespace.
    """
    def construct_counts_key(*keys: str):
        """
        Filters out all falsy values in passed args
        and joins them into a redis `counts:` key string.
        """
        filtered_args = (key for key in keys if key)
        key_string = ":".join(("counts", namespace, *filtered_args))
        return key_string

    return construct_counts_key
