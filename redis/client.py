"""Shim — re-exports valkey.client."""

from valkey.client import *  # noqa: F401, F403
from valkey.client import Valkey as _Valkey
from valkey.client import StrictValkey as _StrictValkey

# redis-py aliases — ``valkey.client`` only exposes the
# ``Valkey``/``StrictValkey`` names, but redis-py consumers may look up
# ``redis.client.StrictRedis`` directly.
Redis = _Valkey
StrictRedis = _StrictValkey
