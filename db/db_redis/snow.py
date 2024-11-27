import logging
import redis
from db.db_redis.connection import create_redis_client, redis_retry

logger = logging.getLogger('db.redis')


@redis_retry()
async def snow_increase(from_tg_user_id: int,
                        *,
                        to_tg_user_id: int = None,
                        from_tg_user_id_amount: int = 1,
                        pattern: str = 'tg_user_id:{}:snow') -> None:
    key_from = pattern.format(from_tg_user_id)
    key_to = pattern.format(to_tg_user_id)

    msg = f'{key_from} throw += {from_tg_user_id_amount}'
    if to_tg_user_id is not None:
        msg += f', {key_to} get += 1'

    logger.info(msg)

    r = await create_redis_client()
    try:

        async with r.pipeline() as pipe:
            await pipe.hincrby(key_from, 'throw', from_tg_user_id_amount)

            if to_tg_user_id is not None:
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
