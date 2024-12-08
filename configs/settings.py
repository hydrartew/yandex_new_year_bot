import random
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: str = str(Path(__file__).parents[1])
    model_config = SettingsConfigDict(env_file=f'{BASE_DIR}/.env', env_file_encoding='utf-8')

    TELEGRAM_BOT_TOKEN: SecretStr
    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str

    YDB_DATABASE: str
    YDB_ENDPOINT: str

    TEST_ENVIRONMENT: bool = False

    REDIS_HOST: str
    REDIS_PASSWORD: SecretStr
    REDIS_PORT: int

    path_ssl_ca_certs: str = f'{BASE_DIR}/configs/.redis/YandexInternalRootCA.crt'

    class SnowSecretBox:
        """Конфигурация шанса выпадения сюрприз бокса для игры ``/snow``"""
        config = {  # TODO: вынести в отдельный json-файл
            "percentage_chance": "0.2%",  # 1/500
            "number_snowballs": {
                "from": 10,
                "to": 100
            }
        }
        percentage_chance = float(config["percentage_chance"].strip('%')) / 100

        @classmethod
        def is_secret_box(cls) -> bool:
            return random.random() < cls.percentage_chance

        @classmethod
        def number_snowballs(cls) -> int:
            return random.randint(cls.config["number_snowballs"]["from"], cls.config["number_snowballs"]["to"])


settings = Settings()
