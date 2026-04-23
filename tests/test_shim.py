"""Tests for the redis → valkey compatibility shim.

Coverage targets:
- redis/__init__.py          — top-level exports, VERSION, metadata patches
- redis/exceptions.py        — RedisError alias
- redis/{client,cluster,connection,credentials,sentinel,lock,retry,backoff,typing,utils}.py
- redis/asyncio/**
- redis/commands/**
- Third-party compat         — kombu, flask-caching
- Live integration           — requires running Valkey on localhost:6379
"""

import importlib
import importlib.metadata
import subprocess
import sys

import pytest
import valkey


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

live = pytest.mark.usefixtures("_check_valkey")


@pytest.fixture(autouse=False)
def _check_valkey(_valkey_reachable):
    if not _valkey_reachable:
        pytest.skip("Valkey not running on localhost:6379")


# ===================================================================
# 1. Top-level redis module exports
# ===================================================================

class TestTopLevelClasses:
    """redis.Redis, redis.StrictRedis, and other class aliases."""

    def test_redis_is_valkey(self):
        import redis
        assert redis.Redis is valkey.Valkey

    def test_strict_redis_is_redis(self):
        import redis
        assert redis.StrictRedis is redis.Redis

    def test_strict_valkey(self):
        import redis
        assert redis.StrictValkey is valkey.StrictValkey

    def test_valkey_class(self):
        import redis
        assert redis.Valkey is valkey.Valkey

    def test_redis_cluster(self):
        import redis
        assert isinstance(redis.RedisCluster, type)

    def test_valkey_cluster(self):
        import redis
        assert redis.ValkeyCluster is valkey.ValkeyCluster


class TestTopLevelConnections:
    """Connection and pool classes."""

    def test_connection(self):
        import redis
        assert redis.Connection is valkey.Connection

    def test_ssl_connection(self):
        import redis
        assert redis.SSLConnection is valkey.SSLConnection

    def test_unix_domain_socket_connection(self):
        import redis
        assert redis.UnixDomainSocketConnection is valkey.UnixDomainSocketConnection

    def test_connection_pool(self):
        import redis
        assert redis.ConnectionPool is valkey.ConnectionPool

    def test_blocking_connection_pool(self):
        import redis
        assert redis.BlockingConnectionPool is valkey.BlockingConnectionPool


class TestTopLevelSentinel:
    """Sentinel classes at top level."""

    def test_sentinel(self):
        import redis
        assert redis.Sentinel is valkey.Sentinel

    def test_sentinel_connection_pool(self):
        import redis
        assert redis.SentinelConnectionPool is valkey.SentinelConnectionPool

    def test_sentinel_managed_connection(self):
        import redis
        assert redis.SentinelManagedConnection is valkey.SentinelManagedConnection

    def test_sentinel_managed_ssl_connection(self):
        import redis
        assert redis.SentinelManagedSSLConnection is valkey.SentinelManagedSSLConnection


class TestTopLevelCredentials:
    """Credential providers at top level."""

    def test_credential_provider(self):
        import redis
        assert redis.CredentialProvider is valkey.CredentialProvider

    def test_username_password_credential_provider(self):
        import redis
        assert redis.UsernamePasswordCredentialProvider is valkey.UsernamePasswordCredentialProvider


class TestTopLevelExceptions:
    """Exception classes re-exported at top level."""

    @pytest.mark.parametrize("name", [
        "AuthenticationError",
        "AuthenticationWrongNumberOfArgsError",
        "BusyLoadingError",
        "ChildDeadlockedError",
        "ConnectionError",
        "DataError",
        "InvalidResponse",
        "OutOfMemoryError",
        "PubSubError",
        "ReadOnlyError",
        "RedisError",
        "ResponseError",
        "TimeoutError",
        "ValkeyError",
        "WatchError",
    ])
    def test_exception_exists(self, name):
        import redis
        cls = getattr(redis, name)
        assert issubclass(cls, Exception)


class TestTopLevelFunctions:
    """Functions and constants at top level."""

    def test_from_url(self):
        import redis
        assert callable(redis.from_url)

    def test_default_backoff(self):
        import redis
        assert callable(redis.default_backoff)


class TestTopLevelVersion:
    """__version__ and VERSION."""

    def test_version_string_matches_valkey(self):
        import redis
        assert redis.__version__ == valkey.__version__

    def test_version_tuple(self):
        import redis
        assert isinstance(redis.VERSION, tuple)
        assert len(redis.VERSION) == 3
        assert all(isinstance(v, int) for v in redis.VERSION)

    def test_version_tuple_matches_string(self):
        import redis
        expected = tuple(int(x) for x in redis.__version__.split("."))
        assert redis.VERSION == expected


# ===================================================================
# 2. Submodule imports
# ===================================================================

class TestSubmoduleImports:
    """Every shim file is importable."""

    @pytest.mark.parametrize("module", [
        "redis.backoff",
        "redis.client",
        "redis.cluster",
        "redis.commands",
        "redis.connection",
        "redis.credentials",
        "redis.exceptions",
        "redis.lock",
        "redis.retry",
        "redis.sentinel",
        "redis.typing",
        "redis.utils",
    ])
    def test_sync_submodule(self, module):
        mod = importlib.import_module(module)
        assert hasattr(mod, "__name__")

    @pytest.mark.parametrize("module", [
        "redis.asyncio",
        "redis.asyncio.client",
        "redis.asyncio.cluster",
        "redis.asyncio.connection",
        "redis.asyncio.lock",
        "redis.asyncio.retry",
        "redis.asyncio.sentinel",
        "redis.asyncio.utils",
    ])
    def test_asyncio_submodule(self, module):
        mod = importlib.import_module(module)
        assert hasattr(mod, "__name__")

    @pytest.mark.parametrize("module", [
        "redis.commands",
        "redis.commands.core",
        "redis.commands.cluster",
        "redis.commands.sentinel",
        "redis.commands.helpers",
        "redis.commands.valkeymodules",
        "redis.commands.redismodules",
        "redis.commands.bf",
        "redis.commands.bf.commands",
        "redis.commands.bf.info",
        "redis.commands.graph",
        "redis.commands.graph.commands",
        "redis.commands.graph.edge",
        "redis.commands.graph.node",
        "redis.commands.graph.path",
        "redis.commands.graph.exceptions",
        "redis.commands.graph.execution_plan",
        "redis.commands.graph.query_result",
        "redis.commands.json",
        "redis.commands.json.commands",
        "redis.commands.json.decoders",
        "redis.commands.json.path",
        "redis.commands.search",
        "redis.commands.search.aggregation",
        "redis.commands.search.commands",
        "redis.commands.search.document",
        "redis.commands.search.field",
        "redis.commands.search.indexDefinition",
        "redis.commands.search.query",
        "redis.commands.search.querystring",
        "redis.commands.search.reducers",
        "redis.commands.search.result",
        "redis.commands.search.suggestion",
        "redis.commands.timeseries",
        "redis.commands.timeseries.commands",
        "redis.commands.timeseries.info",
        "redis.commands.timeseries.utils",
    ])
    def test_commands_submodule(self, module):
        mod = importlib.import_module(module)
        assert hasattr(mod, "__name__")


# ===================================================================
# 3. Submodule attribute access (redis.X.Y)
# ===================================================================

class TestSubmoduleAttributes:
    """Key classes are accessible via redis.submodule.ClassName."""

    def test_redis_dot_client_pipeline(self):
        import redis
        assert isinstance(redis.client.Pipeline, type)

    def test_redis_dot_client_pubsub(self):
        import redis
        assert isinstance(redis.client.PubSub, type)

    def test_sentinel_class(self):
        from redis.sentinel import Sentinel
        assert Sentinel is valkey.sentinel.Sentinel

    def test_lock_class(self):
        from redis.lock import Lock
        assert Lock is valkey.lock.Lock

    def test_retry_class(self):
        from redis.retry import Retry
        assert Retry is valkey.retry.Retry

    def test_backoff_classes(self):
        from redis.backoff import (
            ExponentialBackoff,
            FullJitterBackoff,
            NoBackoff,
        )
        assert callable(ExponentialBackoff)
        assert callable(FullJitterBackoff)
        assert callable(NoBackoff)

    def test_credentials(self):
        from redis.credentials import (
            CredentialProvider,
            UsernamePasswordCredentialProvider,
        )
        assert CredentialProvider is valkey.credentials.CredentialProvider
        assert isinstance(UsernamePasswordCredentialProvider, type)

    def test_connection_pool_from_submodule(self):
        from redis.connection import ConnectionPool
        assert ConnectionPool is valkey.connection.ConnectionPool

    def test_cluster_node(self):
        from redis.cluster import ClusterNode
        assert isinstance(ClusterNode, type)

    def test_async_redis_class(self):
        from redis.asyncio import Redis
        assert isinstance(Redis, type)

    def test_async_connection_pool(self):
        from redis.asyncio.connection import ConnectionPool
        assert isinstance(ConnectionPool, type)

    def test_async_sentinel(self):
        from redis.asyncio.sentinel import Sentinel
        assert isinstance(Sentinel, type)

    def test_async_lock(self):
        from redis.asyncio.lock import Lock
        assert isinstance(Lock, type)

    def test_async_client_strict_redis_attr(self):
        """sentry-sdk dereferences redis.asyncio.client.StrictRedis."""
        import redis.asyncio
        assert redis.asyncio.client.StrictRedis is valkey.asyncio.client.Valkey

    def test_async_client_redis_attr(self):
        import redis.asyncio
        assert redis.asyncio.client.Redis is valkey.asyncio.client.Valkey

    def test_async_client_pipeline_attr(self):
        """sentry-sdk dereferences redis.asyncio.client.Pipeline."""
        import redis.asyncio
        assert redis.asyncio.client.Pipeline is valkey.asyncio.client.Pipeline

    def test_async_cluster_redis_cluster_attr(self):
        """sentry-sdk dereferences redis.asyncio.cluster.RedisCluster."""
        import redis.asyncio
        assert redis.asyncio.cluster.RedisCluster is valkey.asyncio.cluster.ValkeyCluster

    def test_async_cluster_cluster_pipeline_attr(self):
        import redis.asyncio
        assert redis.asyncio.cluster.ClusterPipeline is valkey.asyncio.cluster.ClusterPipeline

    def test_sync_client_strict_redis_attr(self):
        import redis
        assert redis.client.StrictRedis is valkey.client.Valkey

    def test_sync_cluster_redis_cluster_attr(self):
        import redis
        assert redis.cluster.RedisCluster is valkey.cluster.ValkeyCluster


# ===================================================================
# 4. redis.exceptions — compat aliases
# ===================================================================

class TestExceptions:
    """All exception classes importable from redis.exceptions."""

    @pytest.mark.parametrize("name", [
        "AuthenticationError",
        "AuthenticationWrongNumberOfArgsError",
        "AuthorizationError",
        "BusyLoadingError",
        "ChildDeadlockedError",
        "ClusterCrossSlotError",
        "ClusterDownError",
        "ClusterError",
        "ConnectionError",
        "DataError",
        "ExecAbortError",
        "InvalidResponse",
        "LockError",
        "LockNotOwnedError",
        "MasterDownError",
        "MaxConnectionsError",
        "ModuleError",
        "MovedError",
        "NoPermissionError",
        "NoScriptError",
        "OutOfMemoryError",
        "PubSubError",
        "ReadOnlyError",
        "ResponseError",
        "SlotNotCoveredError",
        "TimeoutError",
        "TryAgainError",
        "ValkeyError",
        "WatchError",
    ])
    def test_exception_from_submodule(self, name):
        from redis import exceptions
        cls = getattr(exceptions, name)
        assert issubclass(cls, Exception)

    def test_redis_cluster_exception_alias(self):
        from redis.exceptions import RedisClusterException, ValkeyClusterException
        assert RedisClusterException is ValkeyClusterException

    def test_redis_error_alias(self):
        """RedisError is an alias for ValkeyError in redis.exceptions."""
        from redis.exceptions import RedisError, ValkeyError
        assert RedisError is ValkeyError

    def test_connection_error_hierarchy(self):
        from redis.exceptions import ConnectionError, ValkeyError
        assert issubclass(ConnectionError, ValkeyError)

    def test_timeout_error_hierarchy(self):
        from redis.exceptions import TimeoutError, ValkeyError
        assert issubclass(TimeoutError, ValkeyError)

    def test_lock_error_hierarchy(self):
        from redis.exceptions import LockError, ValkeyError
        assert issubclass(LockError, ValkeyError)


# ===================================================================
# 5. importlib.metadata patches
# ===================================================================

class TestMetadataPatch:
    """importlib.metadata.version('redis') works regardless of import order."""

    def test_direct_version_call(self):
        import redis
        ver = importlib.metadata.version("redis")
        assert ver == redis.__version__

    def test_captured_reference_before_import(self):
        """version() captured before import redis still works (subprocess test)."""
        code = (
            "from importlib.metadata import version as captured; "
            "import redis; "
            "v = captured('redis'); "
            "assert v == redis.__version__, f'{v} != {redis.__version__}'; "
            "print('OK')"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0, result.stderr
        assert "OK" in result.stdout

    def test_distribution_from_name(self):
        """Distribution.from_name('redis') should not raise."""
        import redis  # noqa: F401
        dist = importlib.metadata.Distribution.from_name("redis")
        assert isinstance(dist.metadata["Name"], str)

    def test_other_packages_unaffected(self):
        import redis  # noqa: F401
        assert importlib.metadata.version("valkey") == valkey.__version__

    def test_nonexistent_package_still_raises(self):
        import redis  # noqa: F401
        with pytest.raises(importlib.metadata.PackageNotFoundError):
            importlib.metadata.version("nonexistent-pkg-abc123")

    def test_version_in_subprocess(self):
        """Verify patch works in a fresh interpreter (no test-time side effects)."""
        code = (
            "import redis; "
            "from importlib.metadata import version; "
            "v = version('redis'); "
            "assert v == redis.__version__, f'{v} != {redis.__version__}'; "
            "print('OK')"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0, result.stderr
        assert "OK" in result.stdout


# ===================================================================
# 5b. ConnectionPool.get_connection compatibility with kombu 5.3+
# ===================================================================

class TestConnectionPoolGetConnection:
    """kombu 5.3+ calls pool.get_connection() with no args (redis-py 5.3 signature).

    valkey-py keeps command_name as a required positional, so the shim patches
    ConnectionPool classes to make command_name optional.  Regression guard for
    the TypeError that crashed Celery workers under valkey-redis-compat 0.1.1.
    """

    @pytest.mark.parametrize("dotted", [
        "valkey.connection.ConnectionPool",
        "valkey.connection.BlockingConnectionPool",
        "valkey.asyncio.connection.ConnectionPool",
        "valkey.asyncio.connection.BlockingConnectionPool",
    ])
    def test_command_name_is_optional(self, dotted):
        import redis  # noqa: F401  - activate the patch
        import importlib
        import inspect

        parts = dotted.split(".")
        obj = importlib.import_module(".".join(parts[:-1]))
        cls = getattr(obj, parts[-1])

        sig = inspect.signature(cls.get_connection)
        param = sig.parameters["command_name"]
        assert param.default is not inspect.Parameter.empty, (
            f"{dotted}.get_connection still requires command_name; "
            f"kombu 5.3+ would raise TypeError"
        )

    def test_sync_pool_call_without_args_does_not_raise_type_error(self):
        """Reproduce the exact kombu 5.3+ call — TypeError would mean the patch failed."""
        import redis  # noqa: F401
        from valkey.connection import ConnectionPool

        pool = ConnectionPool(
            host="127.0.0.1",
            port=1,  # unreachable — ConnectionError is fine, TypeError is not
            socket_connect_timeout=0.01,
        )
        try:
            pool.get_connection()
        except TypeError as e:  # pragma: no cover - regression signal
            pytest.fail(f"signature still broken: {e}")
        except Exception:
            # ConnectionError / OSError / etc. — expected and unrelated to this test.
            pass
        finally:
            pool.disconnect()


# ===================================================================
# 6. Third-party compatibility — kombu
# ===================================================================

class TestKombuCompat:
    """kombu redis transport loads and resolves correctly."""

    def test_redis_transport_resolves(self):
        import redis  # noqa: F401
        from kombu.transport import resolve_transport
        transport = resolve_transport("redis")
        assert isinstance(transport, type)

    def test_valkey_transport_alias(self):
        import redis  # noqa: F401
        from kombu.transport import TRANSPORT_ALIASES, resolve_transport
        TRANSPORT_ALIASES.setdefault("valkey", "kombu.transport.redis:Transport")
        transport = resolve_transport("valkey")
        assert isinstance(transport, type)

    def test_kombu_transport_module_level_classes(self):
        """kombu.transport.redis defines classes at module level using redis.*."""
        import redis  # noqa: F401
        from kombu.transport.redis import (
            Transport,
            PrefixedStrictRedis,
        )
        assert isinstance(Transport, type)
        assert issubclass(PrefixedStrictRedis, redis.Redis)

    def test_kombu_redis_version_check(self):
        """kombu checks redis.VERSION at runtime."""
        import redis
        assert redis.VERSION >= (3, 2, 0)


# ===================================================================
# 7. Third-party compatibility — flask-caching
# ===================================================================

class TestFlaskCachingCompat:
    """flask-caching redis backends load without errors."""

    def test_redis_cache_class(self):
        from flask_caching.backends.rediscache import RedisCache
        assert isinstance(RedisCache, type)

    def test_redis_sentinel_cache_class(self):
        from flask_caching.backends.rediscache import RedisSentinelCache
        assert isinstance(RedisSentinelCache, type)

    def test_redis_cluster_cache_class(self):
        from flask_caching.backends.rediscache import RedisClusterCache
        assert isinstance(RedisClusterCache, type)


# ===================================================================
# 8. Identity checks — shim classes ARE valkey classes
# ===================================================================

class TestIdentity:
    """Shim re-exports are the exact same objects, not copies."""

    def test_redis_module_is_not_valkey_path(self):
        import redis
        import valkey
        assert redis.__file__ != valkey.__file__

    @pytest.mark.parametrize("redis_path,valkey_path", [
        ("redis.client.Pipeline", "valkey.client.Pipeline"),
        ("redis.client.PubSub", "valkey.client.PubSub"),
        ("redis.connection.ConnectionPool", "valkey.connection.ConnectionPool"),
        ("redis.sentinel.Sentinel", "valkey.sentinel.Sentinel"),
        ("redis.lock.Lock", "valkey.lock.Lock"),
        ("redis.retry.Retry", "valkey.retry.Retry"),
    ])
    def test_class_identity(self, redis_path, valkey_path):
        """redis.X.Y is valkey.X.Y (same object)."""
        def resolve(dotted):
            parts = dotted.split(".")
            obj = importlib.import_module(parts[0])
            for p in parts[1:]:
                obj = getattr(obj, p)
            return obj

        assert resolve(redis_path) is resolve(valkey_path)


# ===================================================================
# 9. Live integration tests (Valkey on localhost:6379)
# ===================================================================

class TestLiveConnection:
    """Integration tests — require a running Valkey on localhost:6379."""

    @pytest.fixture
    def r(self):
        import redis
        client = redis.Redis(host="localhost", port=6379, db=15)
        try:
            client.ping()
        except Exception:
            pytest.skip("Valkey not available on localhost:6379")
        yield client
        client.flushdb()
        client.close()

    @live
    def test_ping(self, r):
        assert r.ping() is True

    @live
    def test_set_get(self, r):
        r.set("k", "v")
        assert r.get("k") == b"v"

    @live
    def test_set_get_decoded(self):
        import redis
        client = redis.Redis(host="localhost", port=6379, db=15, decode_responses=True)
        try:
            client.ping()
        except Exception:
            pytest.skip("Valkey not available")
        client.set("k2", "hello")
        assert client.get("k2") == "hello"
        client.flushdb()
        client.close()

    @live
    def test_delete(self, r):
        r.set("dk", "x")
        assert r.delete("dk") == 1
        assert r.get("dk") is None

    @live
    def test_mset_mget(self, r):
        r.mset({"a": "1", "b": "2", "c": "3"})
        assert r.mget("a", "b", "c") == [b"1", b"2", b"3"]

    @live
    def test_incr_decr(self, r):
        r.set("counter", 10)
        assert r.incr("counter") == 11
        assert r.decr("counter") == 10

    @live
    def test_expire_ttl(self, r):
        r.set("ttl_key", "x", ex=60)
        ttl = r.ttl("ttl_key")
        assert 0 < ttl <= 60

    @live
    def test_pipeline(self, r):
        pipe = r.pipeline()
        pipe.set("p1", "a")
        pipe.set("p2", "b")
        pipe.get("p1")
        pipe.get("p2")
        results = pipe.execute()
        assert results == [True, True, b"a", b"b"]

    @live
    def test_pipeline_transaction(self, r):
        pipe = r.pipeline(transaction=True)
        pipe.set("tx1", "val")
        pipe.get("tx1")
        results = pipe.execute()
        assert results == [True, b"val"]

    @live
    def test_hash_operations(self, r):
        r.hset("myhash", mapping={"f1": "v1", "f2": "v2"})
        assert r.hget("myhash", "f1") == b"v1"
        assert r.hgetall("myhash") == {b"f1": b"v1", b"f2": b"v2"}

    @live
    def test_list_operations(self, r):
        r.rpush("mylist", "a", "b", "c")
        assert r.lrange("mylist", 0, -1) == [b"a", b"b", b"c"]
        assert r.lpop("mylist") == b"a"

    @live
    def test_set_operations(self, r):
        r.sadd("myset", "a", "b", "c")
        assert r.scard("myset") == 3
        assert r.sismember("myset", "a")

    @live
    def test_sorted_set(self, r):
        r.zadd("zset", {"a": 1, "b": 2, "c": 3})
        assert r.zrange("zset", 0, -1) == [b"a", b"b", b"c"]
        assert r.zscore("zset", "b") == 2.0

    @live
    def test_pubsub(self, r):
        ps = r.pubsub()
        ps.subscribe("test_channel")
        # First message is the subscribe confirmation
        msg = ps.get_message(timeout=1)
        assert msg["type"] == "subscribe"
        ps.unsubscribe()
        ps.close()

    @live
    def test_streams(self, r):
        msg_id = r.xadd("mystream", {"key": "val"})
        assert isinstance(msg_id, bytes)
        messages = r.xrange("mystream")
        assert len(messages) == 1
        assert messages[0][1] == {b"key": b"val"}

    @live
    def test_from_url(self):
        import redis
        client = redis.from_url("redis://localhost:6379/15")
        try:
            assert client.ping() is True
        except Exception:
            pytest.skip("Valkey not available")
        finally:
            client.close()

    @live
    def test_lock(self, r):
        lock = r.lock("test_lock", timeout=5)
        assert lock.acquire(blocking_timeout=1) is True
        lock.release()

    @live
    def test_scan(self, r):
        r.mset({f"scan:{i}": str(i) for i in range(10)})
        keys = []
        for key in r.scan_iter(match="scan:*"):
            keys.append(key)
        assert len(keys) == 10
