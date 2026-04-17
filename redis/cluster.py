"""Shim — re-exports valkey.cluster."""

from valkey.cluster import *  # noqa: F401, F403
from valkey.cluster import ValkeyCluster as _ValkeyCluster

# redis-py alias — sentry-sdk and other redis-py consumers look up
# ``redis.cluster.RedisCluster`` directly.
RedisCluster = _ValkeyCluster
