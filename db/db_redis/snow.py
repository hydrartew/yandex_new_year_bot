import logging
from typing import Literal

import redis
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log

from db.db_redis.connection import r


logger = logging.getLogger('db.redis')


def redis_retry():
    return retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(min=1, max=4),
        before_sleep=before_sleep_log(logger, logging.INFO)
    )


@redis_retry()
async def snow_plus_one(from_tg_user_id: int, to_tg_user_id: int, prefix: str = 'snow') -> None:
    key_from = '{}:from:tg_user_id:{}'.format(prefix, from_tg_user_id)
    key_to = '{}:to:tg_user_id:{}'.format(prefix, to_tg_user_id)

    logger.info(f'/snow {key_from} >> {key_to}')
    try:
        async with r.pipeline(transaction=True) as pipe:
            await (pipe.incr(key_from).incr(key_to).execute())
    except redis.ConnectionError as e:
        logger.error(f'Error connecting to Redis: {e}')
        raise
    except redis.TimeoutError as e:
        logger.error(f'Timeout when trying to connect to Redis: {e}')
        raise
    except Exception as e:
        logger.critical(f"An unexpected error: {e}")
        raise


@redis_retry()
async def get_snow_stats(tg_user_id: int, prefix: str = 'snow') -> tuple[int, int]:
    key_from = '{}:from:tg_user_id:{}'.format(prefix, tg_user_id)
    key_to = '{}:to:tg_user_id:{}'.format(prefix, tg_user_id)

    logger.info(f'/snow stats {tg_user_id}')
    try:
        async with r.pipeline(transaction=True) as pipe:
            value_from, value_to = await (pipe.get(key_from).get(key_to).execute())
    except redis.ConnectionError as e:
        logger.error(f'Error connecting to Redis: {e}')
        raise
    except redis.TimeoutError as e:
        logger.error(f'Timeout when trying to connect to Redis: {e}')
        raise
    except Exception as e:
        logger.critical(f"An unexpected error: {e}")
        raise

    if value_from is None:
        value_from = 0
        logger.warning(f'/snow stats value_from is None for {key_from}')

    if value_to is None:
        value_to = 0
        logger.warning(f'/snow stats value_to is None for {key_to}')

    return value_from, value_to
