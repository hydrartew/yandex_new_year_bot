import asyncio
import json
import logging

import redis

from db.db_redis.connection import create_redis_client, redis_retry

logger = logging.getLogger('db.redis')


@redis_retry()
async def up_snowman_height(tg_user_id: int, height_increase: int, pattern: str = 'tg_user_id:{}:snowman'):
    key = pattern.format(tg_user_id)

    lua_script = """
        local key = KEYS[1]
        local height_increase = tonumber(ARGV[1])
        local value = redis.call('GET', key)
        
        local data
        
        if not value then
            data = {current = height_increase, maximum = height_increase}
        else
            data = cjson.decode(value)            
            data.current = data.current + height_increase
            
            if data.current > data.maximum then
                data.maximum = data.current
            end
        end
        
        redis.call('SET', key, cjson.encode(data))
        return cjson.encode(data)
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
    return json.loads(updated_data)


async def main():
    tg_user_id = 3  # Замените на нужный ID
    height_increase = 3  # Замените на нужное значение
    import time
    start_time = time.time()
    updated_data = await up_snowman_height(tg_user_id, height_increase)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Время выполнения: {execution_time} секунд")
    print(updated_data)


if __name__ == "__main__":
    asyncio.run(main())
