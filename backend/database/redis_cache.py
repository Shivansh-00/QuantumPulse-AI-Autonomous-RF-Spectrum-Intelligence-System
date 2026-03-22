"""Redis cache client for real-time data caching."""
from __future__ import annotations

import json
import logging
from typing import Optional

import redis.asyncio as aioredis
from config import get_settings

logger = logging.getLogger("quantumpulse.redis")


class RedisCache:
    """Async Redis cache wrapper."""

    def __init__(self):
        settings = get_settings()
        self._redis: Optional[aioredis.Redis] = None
        self._url = settings.redis_url

    async def connect(self):
        if self._redis is None:
            self._redis = aioredis.from_url(self._url, decode_responses=True)
            await self._redis.ping()
            logger.info("Redis connected at %s", self._url)

    async def disconnect(self):
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Redis disconnected.")

    async def get(self, key: str) -> Optional[dict]:
        if not self._redis:
            return None
        data = await self._redis.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value: dict, ttl: int = 300):
        if not self._redis:
            return
        await self._redis.set(key, json.dumps(value), ex=ttl)

    async def delete(self, key: str):
        if not self._redis:
            return
        await self._redis.delete(key)

    async def publish(self, channel: str, message: dict):
        if not self._redis:
            return
        await self._redis.publish(channel, json.dumps(message))


cache = RedisCache()
