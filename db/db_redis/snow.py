import logging

import redis

from db.db_redis.connection import create_redis_client, redis_retry
from schemas import SnowRedisData

logger = logging.getLogger('db.redis')


@redis_retry()
async def snow_plus_one(from_tg_user_id: int, to_tg_user_id: int, pattern: str = 'tg_user_id:{}:snow') -> None:
    key_from = pattern.format(from_tg_user_id)
    key_to = pattern.format(to_tg_user_id)

    logger.info(f'/snow {key_from} >> {key_to}')

    r = await create_redis_client()
    try:
        async with r.pipeline() as pipe:
            await pipe.hincrby(key_from, 'throw')
            await pipe.hincrby(key_to, 'get')
            await pipe.execute()
    except redis.ConnectionError as e:
        logger.error(f'Error connecting to Redis: {e}')
        raise
    except redis.TimeoutError as e:
        logger.error(f'Timeout when trying to connect to Redis: {e}')
        raise
    except Exception as e:
        logger.critical(f"An unexpected error: {e}")
        raise
    finally:
        await r.aclose()


@redis_retry()
async def get_snow_stats(tg_user_id: int, pattern: str = 'tg_user_id:{}:snow') -> SnowRedisData:
    key = pattern.format(tg_user_id)

    logger.info(f'/snow stats {tg_user_id}')

    r = await create_redis_client()
    try:
        dict_value = await r.hgetall(key)
    except redis.ConnectionError as e:
        logger.error(f'Error connecting to Redis: {e}')
        raise
    except redis.TimeoutError as e:
        logger.error(f'Timeout when trying to connect to Redis: {e}')
        raise
    except Exception as e:
        logger.critical(f"An unexpected error: {e}")
        raise
    finally:
        await r.aclose()

    if dict_value is None:
        logger.warning(f'/snow stats value is None for {key}')

    return SnowRedisData.model_validate(dict_value) if dict_value else SnowRedisData()
