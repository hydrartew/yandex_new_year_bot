from config_data import settings

import redis.asyncio as aioredis


async def create_redis_client() -> aioredis.StrictRedis:
    return await aioredis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD.get_secret_value(),
        ssl=True,
        ssl_ca_certs=settings.path_ssl_ca_certs,
        decode_responses=True
    )
