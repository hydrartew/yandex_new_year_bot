import random
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from schemas import WhoMoves


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

    class SnowSecretBoxConfig:
        """Конфигурация шанса выпадения сюрприз бокса для игры ``/snow``"""
        config = {  # TODO: обернуть в pydantic модель
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

    class SnowDuelConfig:
        """Конфигурация шансов для игры ``/snow_duel``"""
        config = {  # TODO: обернуть в pydantic модель
            "distance": {
                "bottom_bound": {
                    "steps": 25,  # inclusive
                    "hit_chance": "60%"
                },
                "upper_bound": {
                    "steps": 45,  # inclusive
                    "hit_chance": "40%"
                }
            },
            "chance_first_move": {
                "owner": "50%",
                "opponent": "50%"
            },
            "user_buff": {
                "interval_of_games_played": 20,
                "increase_hit_chance": "1%",
                "max_increase_hit_chance": "15%"
            }
        }

        @classmethod
        def get_random_distance(cls) -> int:
            _config = cls.config['distance']
            return random.randint(_config['bottom_bound']['steps'], _config['upper_bound']['steps'])

        @classmethod
        def hit_chance(cls, distance: int) -> float:
            _config = cls.config['distance']

            upper_steps = _config['upper_bound']['steps']
            bottom_steps = _config['bottom_bound']['steps']

            if not (bottom_steps <= distance <= upper_steps):
                raise ValueError(f"Steps must be between distance.bottom_bound.steps:{bottom_steps} "
                                 f"and distance.upper_bound.steps:{upper_steps}")

            bottom_hit_chance = int(_config['bottom_bound']['hit_chance'].strip('%'))
            upper_hit_chance = int(_config['upper_bound']['hit_chance'].strip('%'))

            chance_1_step = (bottom_hit_chance - upper_hit_chance) / (upper_steps - bottom_steps)

            current_step_hit_chance = bottom_hit_chance - ((distance - bottom_steps) * chance_1_step)

            return round(current_step_hit_chance, 2)

        @staticmethod
        def is_hit(hit_chance: float) -> bool:
            return random.choices([
                True,
                False
            ], weights=[
                hit_chance,
                100 - hit_chance
            ])[0]

        @classmethod
        def who_moves_first(cls) -> WhoMoves:
            _config = cls.config['chance_first_move']

            return random.choices([
                WhoMoves.owner,
                WhoMoves.opponent
            ], weights=[
                int(_config['owner'].strip('%')),
                int(_config['opponent'].strip('%'))
            ])[0]

        @classmethod
        def user_buff(cls, games_played: int) -> float:
            _config = cls.config['user_buff']

            buff = (games_played // _config['interval_of_games_played']) * float(
                _config['increase_hit_chance'].strip('%'))

            max_increase_hit_chance = float(_config['max_increase_hit_chance'].strip('%'))
            if buff > max_increase_hit_chance:
                return max_increase_hit_chance
            return buff


settings = Settings()
