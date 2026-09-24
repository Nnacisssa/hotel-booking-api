import redis.asyncio as aioredis

redis_client = aioredis.from_url(
    "redis://localhost:6379",
    encoding="utf-8",
    decode_responses=True
)