import logging
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log
from configs import settings
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


async def create_redis_client() -> aioredis.StrictRedis:
    return await aioredis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD.get_secret_value(),
        ssl=True,
        ssl_ca_certs=settings.path_ssl_ca_certs,
        decode_responses=True,
        socket_connect_timeout=2
    )


def redis_retry():
    return retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(min=1, max=4),
        before_sleep=before_sleep_log(logger, logging.ERROR, exc_info=True)
    )
