# valkey-redis-compat

Drop-in замена `redis-py` на основе [`valkey-py`](https://github.com/valkey-io/valkey-py).
Мигрируйте с Redis на [Valkey](https://valkey.io/) без изменения кода приложения.

[English version](README.md)

## Что делает пакет

| Слой | До | После |
|---|---|---|
| `import redis` | загружает `redis-py` | загружает `valkey-py` через shim |
| `redis.Redis(...)` | `redis.client.Redis` | `valkey.client.Valkey` (API-совместим) |
| kombu broker transport | только `redis://` | работает через shim |
| flask-caching `RedisCache` | требует `redis-py` | работает через shim |

Пакет патчит `importlib.metadata.version("redis")`, чтобы библиотеки вроде kombu, проверяющие установленную версию redis при импорте, работали без проблем.

## Установка

```bash
pip install valkey-redis-compat
```

## Быстрый старт

В коде приложения ничего не меняется:

```python
import redis

r = redis.Redis(host="localhost", port=6379, db=0)
r.set("key", "value")
print(r.get("key"))  # b'value'
```

Все вызовы прозрачно проходят через `valkey-py`.

### kombu / Celery broker

kombu внутри использует `import redis` для транспорта `redis://` — shim обеспечивает прозрачную работу.

Для использования URL-схемы `valkey://` в качестве брокера зарегистрируйте алиас транспорта до старта Celery:

```python
from kombu.transport import TRANSPORT_ALIASES

TRANSPORT_ALIASES.setdefault("valkey", "kombu.transport.redis:Transport")
TRANSPORT_ALIASES.setdefault("valkeys", "kombu.transport.redis:Transport")
```

### flask-caching

Изменения не требуются — `RedisCache` / `RedisSentinelCache` внутри импортируют `redis`, который предоставляется этим пакетом.

## Покрытие shim-слоя

Все публичные субмодули `valkey-py` реэкспортируются под пространством имён `redis`:

| `redis.*` | отображается на |
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

Вложенные субмодули (`redis.asyncio.client`, `redis.commands.search` и т.д.) также покрыты.

## Почему не просто `import valkey as redis`?

Это работает для **вашего** кода.
Это не работает для **сторонних библиотек** (kombu, flask-caching, celery), которые внутри делают `import redis`.
Этот пакет решает обе проблемы одновременно.

## Совместимость

- Python 3.9 -- 3.13
- valkey-py >= 6.1.1
- Протестировано с kombu 5.x, flask-caching 2.x

## Лицензия

MIT
