import json
import os
import threading
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import redis

_l1 = OrderedDict()
_l1_lock = threading.Lock()
_L1_MAX = 2048

_l2 = None
_l2_pool = None
_l2_unavailable = False

_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="cache-writer")


class _Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


def _l1_get(key):
    with _l1_lock:
        if key not in _l1:
            return None
        value, expiry = _l1[key]
        if time.time() > expiry:
            _l1.pop(key, None)
            return None
        _l1.move_to_end(key)
        return value


def _l1_set(key, value, ttl=300):
    with _l1_lock:
        if key in _l1:
            _l1.move_to_end(key)
        _l1[key] = (value, time.time() + ttl)
        while len(_l1) > _L1_MAX:
            _l1.popitem(last=False)


def _l1_delete(key):
    with _l1_lock:
        _l1.pop(key, None)


def _l1_clear(pattern):
    with _l1_lock:
        keys_to_delete = [k for k in _l1 if k.startswith(pattern)]
        for k in keys_to_delete:
            _l1.pop(k, None)


def get_l2():
    global _l2, _l2_unavailable
    if _l2_unavailable:
        return None
    if _l2 is None:
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        try:
            _l2_pool = redis.ConnectionPool.from_url(
                redis_url,
                max_connections=10,
                socket_timeout=0.5,
                socket_connect_timeout=0.5,
                decode_responses=True,
            )
            _l2 = redis.Redis(connection_pool=_l2_pool)
            _l2.ping()
        except (redis.ConnectionError, redis.TimeoutError, redis.RedisError):
            _l2_unavailable = True
            _l2 = None
    return _l2


def _l2_safe(fn):
    try:
        client = get_l2()
        if client is not None:
            return fn(client)
    except redis.RedisError:
        pass
    return None


def _l2_fire_and_forget(fn):
    try:
        _executor.submit(lambda: _l2_safe(fn))
    except Exception:
        pass


def get_user(user_id):
    key = f"user:{user_id}"
    value = _l1_get(key)
    if value is not None:
        return value

    def _read(client):
        data = client.get(key)
        return json.loads(data) if data else None

    value = _l2_safe(_read)
    if value is not None:
        _l1_set(key, value)
        return value
    return None


def set_user(user_id, data, ttl=300):
    key = f"user:{user_id}"
    _l1_set(key, data, ttl)
    payload = json.dumps(data, cls=_Encoder)
    _l2_fire_and_forget(lambda client: client.setex(key, ttl, payload))


def delete_user(user_id):
    key = f"user:{user_id}"
    _l1_delete(key)
    _l2_fire_and_forget(lambda client: client.delete(key))


def clear_all_users():
    _l1_clear("user:")
    _l2_fire_and_forget(lambda client: client.delete(*client.keys("user:*")))


def get_url(url_id):
    key = f"url:{url_id}"
    value = _l1_get(key)
    if value is not None:
        return value

    def _read(client):
        data = client.get(key)
        return json.loads(data) if data else None

    value = _l2_safe(_read)
    if value is not None:
        _l1_set(key, value)
        return value
    return None


def set_url(url_id, data, ttl=300):
    key = f"url:{url_id}"
    _l1_set(key, data, ttl)
    payload = json.dumps(data, cls=_Encoder)
    _l2_fire_and_forget(lambda client: client.setex(key, ttl, payload))


def delete_url(url_id):
    key = f"url:{url_id}"
    _l1_delete(key)
    _l2_fire_and_forget(lambda client: client.delete(key))


def clear_all_urls():
    _l1_clear("url:")
    _l2_fire_and_forget(lambda client: client.delete(*client.keys("url:*")))
