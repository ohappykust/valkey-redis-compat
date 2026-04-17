"""Shim — re-exports valkey.asyncio.client."""

from valkey.asyncio.client import *  # noqa: F401, F403
from valkey.asyncio.client import Valkey as _Valkey
from valkey.asyncio.client import StrictValkey as _StrictValkey

# redis-py aliases — ``valkey.asyncio.client`` only exposes the
# ``Valkey``/``StrictValkey`` names, but libraries that target redis-py
# (e.g. sentry-sdk) look up ``redis.asyncio.client.StrictRedis`` directly.
Redis = _Valkey
StrictRedis = _StrictValkey
