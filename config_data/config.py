import json
from pathlib import Path

import ydb
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: str = str(Path(__file__).parents[1])
    model_config = SettingsConfigDict(env_file=f'{BASE_DIR}/.env')

    TRACKER_INTERNAL_TOKEN: str
    TRACKER_AMAYAMMI_TOKEN: str

    TELEGRAM_BOT_TOKEN: str

    YDB_DATABASE: str
    YDB_ENDPOINT: str

    TEST_ENVIRONMENT: bool | None = False


settings = Settings()

credentials = ydb.iam.MetadataUrlCredentials()

if settings.TEST_ENVIRONMENT:
    with open(f"{settings.BASE_DIR}/config_data/authorized_key.json", "r+", encoding='utf-8') as f:
        authorized_key = json.load(f)

    iam_token = ydb.iam.ServiceAccountCredentials(
        service_account_id=authorized_key['service_account_id'],
        access_key_id=authorized_key['id'],
        private_key=authorized_key['private_key']
    ).token

    credentials = ydb.credentials.AccessTokenCredentials(token=iam_token)
