import logging
import redis
from db.db_redis.connection import create_redis_client, redis_retry
from schemas import NightKingFlag

logger = logging.getLogger(__name__)


@redis_retry()
async def set_night_king_flag(tg_user_id: int, pattern: str = 'tg_user_id:{}:night_king_flag') -> NightKingFlag:
    key = pattern.format(tg_user_id)

    r = await create_redis_client()
    try:
        logger.info('Getting {}'.format(key))
        flag = await r.get(key)

        if flag is not None:
            logger.info('Flag {} already exists'.format(key))
            return NightKingFlag(already_exists=True)

        logger.info('Flag {} does not exist, setting this'.format(key))
        await r.set(key, 1)

        logger.info('Flag {} is set successfully'.format(key))

        return NightKingFlag(added=True)

    except (redis.ConnectionError, redis.TimeoutError) as e:
        logger.error('Error connecting to Redis while setting flag {}; {}'.format(key, e))
        raise
    except Exception as e:
        logger.critical('An unexpected error while setting flag {}; {}'.format(key, e))
        raise
    finally:
        await r.aclose()
