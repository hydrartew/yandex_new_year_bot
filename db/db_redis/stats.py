import asyncio
import logging

import redis

from db.db_redis.connection import create_redis_client, redis_retry
from schemas import SnowRedisData, SnowmanRedisData, SnowDuelUserStats

logger = logging.getLogger('db.redis')


@redis_retry()
async def get_stats(tg_user_id: int, pattern: str = 'tg_user_id:{}:{}'
                    ) -> tuple[SnowRedisData, SnowmanRedisData, SnowDuelUserStats]:
    logger.info(f'Getting stats for tg_user_id:{tg_user_id}')

    r = await create_redis_client()
    try:
        async with r.pipeline() as pipe:
            await pipe.hgetall(pattern.format(tg_user_id, 'snow'))
            await pipe.hgetall(pattern.format(tg_user_id, 'snowman'))
            await pipe.hgetall(pattern.format(tg_user_id, 'snow_duel'))

            data = await pipe.execute()

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

    logger.info('Stats for tg_user_id:{} received: {}'.format(tg_user_id, data))

    return (
        SnowRedisData.model_validate(data[0]),
        SnowmanRedisData.model_validate(data[1]),
        SnowDuelUserStats.model_validate(data[2])
    )


async def main():
    print(await get_stats(861493335))


if __name__ == "__main__":
    asyncio.run(main())
