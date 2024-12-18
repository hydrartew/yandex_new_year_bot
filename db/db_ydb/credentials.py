import json
import time

import ydb
from configs import settings

import logging.config

logger = logging.getLogger(__name__)


class CredentialsManager:
    def __init__(self):
        self.token = None
        self.token_expiration = None
        self.file_path = '{}/configs/authorized_key.json'.format(settings.BASE_DIR)

    def get_credentials(self):
        if settings.TEST_ENVIRONMENT:
            if self.token is None or self.is_token_expired:
                self.refresh_token()
            return ydb.credentials.AccessTokenCredentials(token=self.token)
        else:
            return ydb.iam.MetadataUrlCredentials()

    def refresh_token(self):
        logger.info('Getting IAM token')
        try:
            self.token = ydb.iam.ServiceAccountCredentials.from_file(self.file_path).token
        except FileNotFoundError:
            logger.error(f"File not found: {self.file_path}")
            raise
        except (json.JSONDecodeError, KeyError):
            logger.error(f"Bad json in file {self.file_path}")
            raise
        except Exception as e:
            logger.error(f"Error refreshing IAM token: {e}")
            raise
        self.token_expiration = time.time() + 1800
        logger.info("IAM token retrieved successfully")

    @property
    def is_token_expired(self):
        if self.token_expiration is None:
            return True
        return time.time() >= self.token_expiration


credentials_manager = CredentialsManager()
