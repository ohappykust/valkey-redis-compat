"""Shim — re-exports valkey.asyncio."""

from valkey.asyncio import *  # noqa: F401, F403

# Re-export local shim submodules so that attribute access like
# ``redis.asyncio.client``, ``redis.asyncio.connection``, etc. works
# (required by sentry-sdk's Redis integration, among others).  Using the
# local shims (not ``valkey.asyncio.*``) lets those shims add
# redis-specific aliases such as ``StrictRedis``.
from . import client  # noqa: F401
from . import cluster  # noqa: F401
from . import connection  # noqa: F401
from . import lock  # noqa: F401
from . import retry  # noqa: F401
from . import sentinel  # noqa: F401
from . import utils  # noqa: F401
