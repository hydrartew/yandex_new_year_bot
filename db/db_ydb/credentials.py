import json


import ydb

from config_data import settings

import logging.config

logging.config.fileConfig('logging.ini')
logger = logging.getLogger('db.ydb')
logging.getLogger('db.ydb').propagate = False


def load_authorized_key() -> dict:
    file_path = f"{settings.BASE_DIR}/config_data/authorized_key.json"
    try:
        with open(file_path, "r+", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from file: {file_path}")
        raise


def get_credentials():
    if settings.TEST_ENVIRONMENT:
        authorized_key = load_authorized_key()

        logger.info('Getting IAM token')

        iam_token = ydb.iam.ServiceAccountCredentials(
            service_account_id=authorized_key['service_account_id'],
            access_key_id=authorized_key['id'],
            private_key=authorized_key['private_key']
        ).token

        logger.info("IAM token retrieved successfully")

        return ydb.credentials.AccessTokenCredentials(token=iam_token)

    return ydb.iam.MetadataUrlCredentials()


credentials = get_credentials()
