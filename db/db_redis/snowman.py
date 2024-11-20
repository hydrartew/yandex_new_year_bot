import asyncio
import json
import logging

import redis

from db.db_redis.connection import create_redis_client, redis_retry
from schemas import SnowmanHeightRedisData

logger = logging.getLogger('db.redis')


@redis_retry()
async def update_snowman(tg_user_id: int, height_increase: int,
                         pattern: str = 'tg_user_id:{}:snowman') -> SnowmanHeightRedisData:
    key = pattern.format(tg_user_id)

    lua_script = """
        local key = KEYS[1]
        local height_increase = tonumber(ARGV[1])

        local values = redis.call('HMGET', key, 'all_attempts', 'current', 'maximum')

        local all_attempts = tonumber(values[1]) or 0
        local current = tonumber(values[2]) or 0
        local maximum = tonumber(values[3]) or current

        all_attempts = all_attempts + 1

        if height_increase < 0 then
            current = 0
        else
            current = current + height_increase
            if current > maximum then
                maximum = current
            end
        end

        redis.call('HMSET', key, 'all_attempts', all_attempts, 'current', current, 'maximum', maximum)
        return cjson.encode({all_attempts = all_attempts, current = current, maximum = maximum})
    """

    logger.info(f'/snowman {key}')

    r = await create_redis_client()
    try:
        updated_data = await r.eval(lua_script, 1, key, str(height_increase))
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
    return SnowmanHeightRedisData.model_validate((json.loads(updated_data)))


@redis_retry()
async def get_snowman(tg_user_id: int, pattern: str = 'tg_user_id:{}:snowman') -> SnowmanHeightRedisData:
    key = pattern.format(tg_user_id)

    logger.info(f'/snowman stats {tg_user_id}')

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
        logger.warning(f'/snowman stats value is None for {key}')

    return SnowmanHeightRedisData.model_validate(dict_value) if dict_value else SnowmanHeightRedisData()
