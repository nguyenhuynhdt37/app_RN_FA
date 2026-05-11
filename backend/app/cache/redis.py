"""
Redis client + async cache decorator.

Usage:
    @cache(ttl=300, key_prefix="restaurant_list")
    async def get_restaurants(self, page: int) -> list[dict]:
        ...
"""

from __future__ import annotations

import functools
import json
from collections.abc import Callable
from typing import Any

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging import logger

# ─── Client ────────────────────────────────────────────────────────────────────
redis_client: aioredis.Redis = aioredis.from_url(
    str(settings.REDIS_URL),
    decode_responses=True,
    encoding="utf-8",
)


# ─── Decorator ─────────────────────────────────────────────────────────────────
def cache(ttl: int = 300, key_prefix: str = "") -> Callable:
    """
    Async cache decorator for service methods.
    - Serializes return value as JSON.
    - Cache key = "{key_prefix or func_name}:{args}:{kwargs}".
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            prefix = key_prefix or func.__qualname__
            cache_key = f"{prefix}:{args[1:]}:{sorted(kwargs.items())}"

            try:
                cached = await redis_client.get(cache_key)
                if cached is not None:
                    logger.debug("cache.hit", key=cache_key)
                    return json.loads(cached)
            except Exception as exc:  # noqa: BLE001
                logger.warning("cache.read_error", key=cache_key, error=str(exc))

            result = await func(*args, **kwargs)

            try:
                await redis_client.setex(
                    cache_key, ttl, json.dumps(result, default=str)
                )
                logger.debug("cache.set", key=cache_key, ttl=ttl)
            except Exception as exc:  # noqa: BLE001
                logger.warning("cache.write_error", key=cache_key, error=str(exc))

            return result

        return wrapper

    return decorator


# ─── Invalidation ──────────────────────────────────────────────────────────────
async def invalidate_pattern(pattern: str) -> int:
    """Delete all Redis keys matching a glob pattern. Returns count deleted."""
    try:
        keys: list[str] = await redis_client.keys(pattern)
        if keys:
            deleted: int = await redis_client.delete(*keys)
            logger.info("cache.invalidate", pattern=pattern, deleted=deleted)
            return deleted
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.error("cache.invalidate_error", pattern=pattern, error=str(exc))
        return 0
