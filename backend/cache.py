import hashlib
import json
import os
from typing import Any

try:
    import redis
except Exception:  # pragma: no cover - optional dependency
    redis = None


_CACHE_MEMORY: dict[str, Any] = {}
CACHE_PREFIX = "dynamic_pricing:"
DEFAULT_TTL_SECONDS = 300
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))


def make_cache_key(prefix: str, payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    return f"{CACHE_PREFIX}{prefix}:{digest}"


def get_cache(key: str) -> Any:
    if redis is not None:
        try:
            client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
            value = client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception:
            return _CACHE_MEMORY.get(key)

    return _CACHE_MEMORY.get(key)


def set_cache(key: str, value: Any, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
    if redis is not None:
        try:
            client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
            client.set(key, json.dumps(value, default=str), ex=ttl_seconds)
            return
        except Exception:
            pass

    _CACHE_MEMORY[key] = value
