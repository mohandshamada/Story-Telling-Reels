"""Redis pub/sub helper for job progress notifications."""

import json
import logging
from typing import Any

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisPubSub:
    def __init__(self):
        self._redis: aioredis.Redis | None = None

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        return self._redis

    async def publish(self, job_id: str, message: dict[str, Any]) -> None:
        try:
            redis = await self._get_redis()
            await redis.publish(f"job:{job_id}", json.dumps(message))
        except Exception as exc:
            logger.debug("Redis publish failed: %s", exc)

    async def subscribe(self, job_id: str):
        redis = await self._get_redis()
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"job:{job_id}")
        return pubsub


redis_pubsub = RedisPubSub()
