from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
import redis.asyncio as aioredis

from config_data import settings

storage = RedisStorage(
    redis=aioredis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD.get_secret_value(),
        ssl=True,
        ssl_ca_certs=settings.path_ssl_ca_certs,
        decode_responses=True
    )
)

dp = Dispatcher(storage=storage)
