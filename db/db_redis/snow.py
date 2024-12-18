import logging
import redis
from db.db_redis.connection import create_redis_client, redis_retry

logger = logging.getLogger(__name__)


@redis_retry()
async def snow_increase(from_tg_user_id: int,
                        *,
                        to_tg_user_id: int = None,
                        from_tg_user_id_amount: int = 1,
                        pattern: str = 'tg_user_id:{}:snow') -> None:
    key_from = pattern.format(from_tg_user_id)
    key_to = pattern.format(to_tg_user_id)

    log_msg = '{} throw += {}'.format(key_from, from_tg_user_id_amount)
    if to_tg_user_id is not None:
        log_msg += ', {} get += 1'.format(key_to)

    r = await create_redis_client()
    try:

        async with r.pipeline() as pipe:
            await pipe.hincrby(key_from, 'throw', from_tg_user_id_amount)

            if to_tg_user_id is not None:
                await pipe.hincrby(key_to, 'get')

            await pipe.execute()

    except (redis.ConnectionError, redis.TimeoutError) as e:
        logger.error('Error connecting to Redis while key_from: {}'.format(
            log_msg, e
        ))
        raise
    except Exception as e:
        logger.critical('An unexpected error while {}: {}'.format(
            log_msg, e
        ))
        raise
    finally:
        await r.aclose()
