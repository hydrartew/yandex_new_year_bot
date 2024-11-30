from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: str = str(Path(__file__).parents[1])
    model_config = SettingsConfigDict(env_file=f'{BASE_DIR}/.env', env_file_encoding='utf-8')

    TELEGRAM_BOT_TOKEN: SecretStr

    YDB_DATABASE: str
    YDB_ENDPOINT: str

    TEST_ENVIRONMENT: bool = False

    REDIS_HOST: str
    REDIS_PASSWORD: SecretStr
    REDIS_PORT: int

    path_ssl_ca_certs: str = f'{BASE_DIR}/configs/.redis/YandexInternalRootCA.crt'


settings = Settings()
