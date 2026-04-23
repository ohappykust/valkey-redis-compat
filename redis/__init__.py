"""Redis compatibility shim — all imports are backed by valkey-py."""

from valkey import *  # noqa: F401, F403
from valkey import VERSION  # noqa: F401
from valkey import __version__  # noqa: F401

# Re-export submodules so that attribute access like ``redis.client``,
# ``redis.connection``, etc. works (required by kombu, flask-caching, celery).
from valkey import asyncio  # noqa: F401
from valkey import backoff  # noqa: F401
from valkey import client  # noqa: F401
from valkey import cluster  # noqa: F401
from valkey import commands  # noqa: F401
from valkey import connection  # noqa: F401
from valkey import credentials  # noqa: F401
from valkey import exceptions  # noqa: F401
from valkey import lock  # noqa: F401
from valkey import retry  # noqa: F401
from valkey import sentinel  # noqa: F401
from valkey import typing  # noqa: F401
from valkey import utils  # noqa: F401

# ---------------------------------------------------------------------------
# importlib.metadata compatibility
# ---------------------------------------------------------------------------
# Libraries like kombu do ``from importlib.metadata import version`` at module
# level and call ``version("redis")`` to decide API behaviour.  When this shim
# is installed under the dist-name *valkey-redis-compat* there is no
# ``redis`` dist-info, so the call raises ``PackageNotFoundError`` (a subclass
# of ``ImportError``) and kombu sets ``redis = None``.
#
# We apply two patches:
#   1. ``importlib.metadata.version`` — intercepts direct calls.
#   2. ``Distribution.from_name`` — intercepts callers that captured a
#      reference to ``version()`` before this module was imported (the
#      function internally calls ``Distribution.from_name``).
#
# NOTE: The attribute swaps are atomic under CPython's GIL (single
# STORE_ATTR opcode) so concurrent threads will not see a half-patched
# state.  However, there is a tiny window between the two patches where
# only the first is active — acceptable in practice.
# ---------------------------------------------------------------------------
import importlib.metadata as _metadata

_original_version = _metadata.version


def _patched_version(name: str) -> str:
    if name == "redis":
        return __version__
    return _original_version(name)


_metadata.version = _patched_version

# Patch ``Distribution.from_name`` so that callers who already captured a
# reference to the original ``version()`` still get the right answer —
# ``version()`` internally calls ``Distribution.from_name(name).metadata``.
try:
    _OriginalDistribution = _metadata.Distribution
    _original_from_name = _OriginalDistribution.from_name.__func__

    @classmethod  # type: ignore[misc]
    def _patched_from_name(cls, name: str):  # type: ignore[no-untyped-def]
        if name == "redis":
            return _original_from_name(cls, "valkey")
        return _original_from_name(cls, name)

    _OriginalDistribution.from_name = _patched_from_name  # type: ignore[assignment]
except (AttributeError, TypeError):
    # If Distribution.from_name is not a classmethod with __func__
    # (e.g. future Python changes), fall back to the version() patch only.
    pass


# ---------------------------------------------------------------------------
# ConnectionPool.get_connection compatibility
# ---------------------------------------------------------------------------
# kombu >= 5.3.0 inspects ``importlib.metadata.version("redis")`` and, when
# the result is >= 5.3.0, calls ``pool.get_connection()`` without arguments —
# matching the signature introduced in redis-py 5.3.0 which dropped the
# required ``command_name`` argument.  valkey-py (through 6.1.x) still
# defines the method with ``command_name`` as a required positional, which
# makes the kombu call raise:
#     TypeError: ConnectionPool.get_connection() missing 1 required
#     positional argument: 'command_name'
# and prevents Celery workers from starting.
#
# Because we announce ``version("redis") == valkey.__version__`` (so the
# Redis class identity tests pass), the fix lives here: make ``command_name``
# optional on both sync and async ConnectionPool classes.  Passing ``"_"``
# as a placeholder is exactly what kombu < 5.3.0 has always done.
# ---------------------------------------------------------------------------
import functools as _functools
import inspect as _inspect


# Copy identifying attributes but NOT ``__wrapped__`` — otherwise
# ``inspect.signature`` follows it and keeps reporting the original
# (required-argument) signature, masking the patch.
_WRAPPER_ATTRS = ("__module__", "__name__", "__qualname__", "__doc__")


def _make_command_name_optional(pool_cls):
    original = pool_cls.get_connection
    if getattr(original, "__valkey_compat_patched__", False):
        return
    if _inspect.iscoroutinefunction(original):
        async def _wrapper(self, command_name="_", *keys, **options):
            return await original(self, command_name, *keys, **options)
    else:
        def _wrapper(self, command_name="_", *keys, **options):
            return original(self, command_name, *keys, **options)
    _functools.update_wrapper(_wrapper, original, assigned=_WRAPPER_ATTRS, updated=())
    # update_wrapper always sets __wrapped__; drop it so inspect.signature
    # reports the new (optional-command_name) signature.
    try:
        del _wrapper.__wrapped__
    except AttributeError:  # pragma: no cover
        pass
    _wrapper.__valkey_compat_patched__ = True
    pool_cls.get_connection = _wrapper


from valkey.connection import (  # noqa: E402
    BlockingConnectionPool as _BlockingPool,
    ConnectionPool as _SyncPool,
)

_make_command_name_optional(_SyncPool)
_make_command_name_optional(_BlockingPool)

try:
    from valkey.asyncio.connection import (  # noqa: E402
        BlockingConnectionPool as _AsyncBlockingPool,
        ConnectionPool as _AsyncPool,
    )
except ImportError:  # pragma: no cover - asyncio submodule always present in valkey-py
    pass
else:
    _make_command_name_optional(_AsyncPool)
    _make_command_name_optional(_AsyncBlockingPool)
