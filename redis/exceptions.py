"""Shim — re-exports valkey.exceptions with redis-py compat aliases."""

from valkey.exceptions import *  # noqa: F401, F403
from valkey.exceptions import ValkeyClusterException as RedisClusterException  # noqa: F401
from valkey.exceptions import ValkeyError as RedisError  # noqa: F401
