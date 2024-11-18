# import logging
import logging.config
import redis
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log

from config_data import settings
from db.db_redis.connection import r


logging.config.fileConfig(f'{settings.BASE_DIR}/logging.ini')
logging.getLogger('db.redis').propagate = False
logger = logging.getLogger('db.redis')


@retry(
    stop=stop_after_attempt(5),  # Максимальное количество попыток
    wait=wait_exponential(min=1, max=4),  # Экспоненциальная задержка между попытками
    before_sleep=before_sleep_log(logger, logging.INFO)  # Логирование перед каждой попыткой
)
def snow_plus_one(tg_user_id: int, prefix: str = 'tg_user_id'):
    key = '{}:{}'.format(prefix, tg_user_id)

    logger.info(f'/snow {key}')
    try:
        r.incr(key)
    except redis.ConnectionError as e:
        logger.error(f'Error connecting to Redis: {e}')
        raise
    except redis.TimeoutError as e:
        logger.error(f'Timeout when trying to connect to Redis: {e}')
        raise
    except Exception as e:
        logger.critical(f"An unexpected error: {e}")
        raise


snow_plus_one(123)
