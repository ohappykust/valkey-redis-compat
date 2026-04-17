"""Shim — re-exports valkey.asyncio.cluster."""

from valkey.asyncio.cluster import *  # noqa: F401, F403
from valkey.asyncio.cluster import ValkeyCluster as _ValkeyCluster

# redis-py alias — sentry-sdk and other redis-py consumers look up
# ``redis.asyncio.cluster.RedisCluster`` directly.
RedisCluster = _ValkeyCluster
