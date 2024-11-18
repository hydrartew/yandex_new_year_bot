import json
from pathlib import Path

import ydb
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: str = str(Path(__file__).parents[1])
    model_config = SettingsConfigDict(env_file=f'{BASE_DIR}/.env', env_file_encoding='utf-8')

    TRACKER_INTERNAL_TOKEN: SecretStr
    TRACKER_AMAYAMMI_TOKEN: SecretStr

    TELEGRAM_BOT_TOKEN: SecretStr

    YDB_DATABASE: str
    YDB_ENDPOINT: str

    TEST_ENVIRONMENT: bool = False

    REDIS_HOST: str
    REDIS_PASSWORD: SecretStr
    REDIS_PORT: int

    path_ssl_ca_certs: str = f'{BASE_DIR}/.redis/YandexInternalRootCA.crt'


settings = Settings()

credentials = ydb.iam.MetadataUrlCredentials()

# TODO: переместить в db

if settings.TEST_ENVIRONMENT:
    with open(f"{settings.BASE_DIR}/config_data/authorized_key.json", "r+", encoding='utf-8') as f:
        authorized_key = json.load(f)

    iam_token = ydb.iam.ServiceAccountCredentials(
        service_account_id=authorized_key['service_account_id'],
        access_key_id=authorized_key['id'],
        private_key=authorized_key['private_key']
    ).token

    credentials = ydb.credentials.AccessTokenCredentials(token=iam_token)
#