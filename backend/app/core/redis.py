from __future__ import annotations

import redis.asyncio as redis
from app.core.config import settings

# Khởi tạo Redis client
# Dùng decode_responses=True để nhận về string thay vì bytes
redis_client: redis.Redis = redis.from_url(
    str(settings.REDIS_URL),
    decode_responses=True,
    encoding="utf-8",
)

async def get_redis():
    """Dependency cung cấp redis_client cho FastAPI."""
    return redis_client
