import json
import ydb
from config_data import settings

import logging.config

logging.config.fileConfig('logging.ini')
logger = logging.getLogger('db.ydb')
logging.getLogger('db.ydb').propagate = False


def get_credentials():
    file_path = f"{settings.BASE_DIR}/config_data/authorized_key.json"

    if settings.TEST_ENVIRONMENT:
        logger.info('Getting IAM token')
        try:
            iam_token = ydb.iam.ServiceAccountCredentials.from_file(file_path).token
            logger.info("IAM token retrieved successfully")
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except (json.JSONDecodeError, KeyError):
            logger.error(f"Bad json: {file_path}")
            raise

        return ydb.credentials.AccessTokenCredentials(token=iam_token)

    return ydb.iam.MetadataUrlCredentials()
