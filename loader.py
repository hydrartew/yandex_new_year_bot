from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
import redis.asyncio as aioredis

from configs import settings

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

bot = Bot(settings.TELEGRAM_BOT_TOKEN.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)
