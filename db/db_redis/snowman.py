import json
import logging

import redis

from db.db_redis.connection import create_redis_client, redis_retry
from schemas import SnowmanRedisData

logger = logging.getLogger(__name__)


@redis_retry()
async def update_snowman(tg_user_id: int, height_increased: int,
                         pattern: str = 'tg_user_id:{}:snowman') -> SnowmanRedisData:
    key = pattern.format(tg_user_id)

    lua_script = """
        local key = KEYS[1]
        local height_increased = tonumber(ARGV[1])

        local values = redis.call('HMGET', key, 'all_attempts', 'current', 'maximum')

        local all_attempts = tonumber(values[1]) or 0
        local current = tonumber(values[2]) or 0
        local maximum = tonumber(values[3]) or current

        all_attempts = all_attempts + 1

        if height_increased < 0 then
            current = 0
        else
            current = current + height_increased
            if current > maximum then
                maximum = current
            end
        end

        redis.call('HMSET', key, 'all_attempts', all_attempts, 'current', current, 'maximum', maximum)
        return cjson.encode({all_attempts = all_attempts, current = current, maximum = maximum})
    """

    logger.info('tg_user_id:{} updates the snowman with height_increased: {}'.format(tg_user_id, height_increased))

    r = await create_redis_client()
    try:
        updated_data = await r.eval(lua_script, 1, key, str(height_increased))
        return SnowmanRedisData.model_validate_json(updated_data)
    except (redis.ConnectionError, redis.TimeoutError) as e:
        logger.error('Error connecting to Redis while tg_user_id:{} updates the snowman: {}'.format(
            tg_user_id, e
        ))
        raise
    except Exception as e:
        logger.critical('An unexpected error while tg_user_id:{} updates the snowman: {}'.format(
            tg_user_id, e
        ))
        raise
    finally:
        await r.aclose()
