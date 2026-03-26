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
