import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MockRedis:
    """Fallback when Redis is not available."""
    async def publish(self, channel: str, message: str):
        logger.debug(f"[MockRedis] publish {channel}: {message[:100]}")

    async def get(self, key: str):
        return None

    async def set(self, key: str, value: str, ex: int = 0):
        pass

    def pubsub(self):
        return MockPubSub()


class MockPubSub:
    async def subscribe(self, *channels):
        pass

    async def listen(self):
        return
        yield  # noqa: make it an async generator


redis_client: object

if settings.REDIS_URL:
    try:
        import redis.asyncio as aioredis
        redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    except Exception as e:
        logger.warning(f"Redis unavailable, using mock: {e}")
        redis_client = MockRedis()
else:
    redis_client = MockRedis()


async def get_redis():
    return redis_client
