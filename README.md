# valkey-redis-compat

Drop-in `redis-py` replacement backed by [`valkey-py`](https://github.com/valkey-io/valkey-py).
Migrate from Redis to [Valkey](https://valkey.io/) without changing a single line of application code.

[Русская версия / Russian version](README.ru.md)

## What it does

| Layer | Before | After |
|---|---|---|
| `import redis` | loads `redis-py` | loads `valkey-py` via this shim |
| `redis.Redis(...)` | `redis.client.Redis` | `valkey.client.Valkey` (API-compatible) |
| kombu broker transport | `redis://` only | works through the shim |
| flask-caching `RedisCache` | needs `redis-py` | works through the shim |

The package patches `importlib.metadata.version("redis")` so that libraries like kombu, which check the installed redis version at import time, work without issues.

## Installation

```bash
pip install valkey-redis-compat
```

## Quick start

Nothing changes in your application code:

```python
import redis

r = redis.Redis(host="localhost", port=6379, db=0)
r.set("key", "value")
print(r.get("key"))  # b'value'
```

Under the hood every call goes through `valkey-py`.

### kombu / Celery broker

kombu uses `import redis` internally for the `redis://` broker transport — the shim handles this transparently.

To use `valkey://` URLs as a broker, register the transport alias before Celery starts:

```python
from kombu.transport import TRANSPORT_ALIASES

TRANSPORT_ALIASES.setdefault("valkey", "kombu.transport.redis:Transport")
TRANSPORT_ALIASES.setdefault("valkeys", "kombu.transport.redis:Transport")
```

### flask-caching

No changes needed — `RedisCache` / `RedisSentinelCache` import `redis` internally, which this package provides.

## Shim coverage

Every public `valkey-py` submodule is re-exported under the `redis` namespace:

| `redis.*` | maps to |
|---|---|
| `redis` | `valkey` |
| `redis.asyncio` | `valkey.asyncio` |
| `redis.backoff` | `valkey.backoff` |
| `redis.client` | `valkey.client` |
| `redis.cluster` | `valkey.cluster` |
| `redis.commands` | `valkey.commands` |
| `redis.connection` | `valkey.connection` |
| `redis.credentials` | `valkey.credentials` |
| `redis.exceptions` | `valkey.exceptions` |
| `redis.lock` | `valkey.lock` |
| `redis.retry` | `valkey.retry` |
| `redis.sentinel` | `valkey.sentinel` |
| `redis.typing` | `valkey.typing` |
| `redis.utils` | `valkey.utils` |

Nested submodules (`redis.asyncio.client`, `redis.commands.search`, etc.) are also covered.

## Why not just `import valkey as redis`?

That works for **your** code.
It does not work for **third-party libraries** (kombu, flask-caching, celery) that hardcode `import redis` internally.
This package solves both cases at once.

## Compatibility

- Python 3.9 -- 3.13
- valkey-py >= 6.1.1
- Tested with kombu 5.x, flask-caching 2.x

## License

MIT
