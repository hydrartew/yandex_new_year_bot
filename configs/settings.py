import random
from pathlib import Path

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from schemas import SettingsConfigSnow, NumberSnowballs, SettingsConfigSnowDuel, Distance, BottomBound, \
    UpperBound, ChanceFirstMove, UserBuff, Percentage, percentage_to_float, SettingsConfigSnowman


class Settings(BaseSettings):
    BASE_DIR: str = str(Path(__file__).parents[1])

    model_config = SettingsConfigDict(env_file=f'{BASE_DIR}/.env', env_file_encoding='utf-8')

    TELEGRAM_BOT_TOKEN: SecretStr
    TELEGRAM_BOT_LOGIN: str = 'bot_name'

    TELEGRAM_API_ID: int | None = None
    TELEGRAM_API_HASH: str | None = None

    TELEGRAM_CHANNEL_BOT_NEWS_NAME: str = 'Bot News'
    TELEGRAM_CHANNEL_BOT_NEWS_CHAT_ID: int | None = None
    TELEGRAM_CHANNEL_BOT_NEWS_INVITE_LINK: str = 'https://t.me/'
    TELEGRAM_BOT_CREATOR_ID: int = 0

    YANDEX_FORM_FEEDBACK_LINK: str = 'https://forms.yandex.ru/'
    YANDEX_FORM_FEEDBACK_LINK_WITH_PRE_COMPLETION: str = 'https://forms.yandex.ru/'

    YDB_DATABASE: str
    YDB_ENDPOINT: str
    YDB_ROOT_DIR_NAME: str = 'main'

    # True if the app is hosted on Yandex Cloud else False
    BOT_HOST_FOR_YDB_IN_YANDEX_CLOUD: bool = False

    REDIS_HOST: str
    REDIS_PASSWORD: SecretStr
    REDIS_PORT: int

    PREDICTION_TIMEOUT_IN_HOURS: int = 12
    NIGHT_KING_LOSS_THRESHOLD_TO_GET_ACHIEVEMENT: int = 50

    CHAT_IDS_WHITE_LIST: list[int] | None = None
    CHAT_IDS_BLACK_LIST: list[int] | None = None

    path_ssl_ca_certs: str = f'{BASE_DIR}/configs/.redis/YandexInternalRootCA.crt'

    static_json_path: str = f'{BASE_DIR}/static/json/'

    @computed_field
    @property
    def TELEGRAM_CHANNEL_BOT_NEWS_INVITE_HYPERLINK(self) -> str:
        return '<a href="{}">{}</a>'.format(
            self.TELEGRAM_CHANNEL_BOT_NEWS_INVITE_LINK, self.TELEGRAM_CHANNEL_BOT_NEWS_NAME
        )

    class ConfigSnowSecretBox:
        """Конфигурация шанса выпадения сюрприз бокса для игры ``/snow``"""
        config = SettingsConfigSnow(
            percentage_chance='0.2%',  # 1/500
            number_snowballs=NumberSnowballs(
                from_=10,
                to=100
            )
        )

        @classmethod
        def is_secret_box(cls) -> bool:
            return random.random() < cls.config.percentage_chance

        @classmethod
        def number_snowballs(cls) -> int:
            return random.randint(cls.config.number_snowballs.from_, cls.config.number_snowballs.to)

    class ConfigSnowDuel:
        """Конфигурация шансов для игры ``/snow_duel``"""
        config = SettingsConfigSnowDuel(
            distance=Distance(
                bottom_bound=BottomBound(
                    steps=25,
                    hit_chance="60%"
                ),
                upper_bound=UpperBound(
                    steps=45,
                    hit_chance="40%"
                )
            ),
            chance_first_move=ChanceFirstMove(
                owner="50%",
                # opponent=(1-owner)
            ),
            user_buff=UserBuff(
                interval_of_games_played=17,
                increase_hit_chance="1%",
                max_increase_hit_chance="15%"
            )
        )

        @classmethod
        def get_random_distance(cls) -> int:
            return random.randint(
                cls.config.distance.bottom_bound.steps, cls.config.distance.upper_bound.steps
            )

        @classmethod
        def hit_chance(cls, distance: int) -> float:
            _config = cls.config.distance
            upper_steps = _config.upper_bound.steps
            bottom_steps = _config.bottom_bound.steps

            if not (bottom_steps <= distance <= upper_steps):
                raise ValueError(
                    "Distance must be between config.distance.bottom_bound.steps:{} "
                    "and config.distance.upper_bound.steps:{}"
                    .format(bottom_steps, upper_steps)
                )

            bottom_hit_chance = _config.bottom_bound.hit_chance
            upper_hit_chance = _config.upper_bound.hit_chance

            # Calculating the chance for this distance
            chance_per_step = (bottom_hit_chance - upper_hit_chance) / (upper_steps - bottom_steps)
            current_step_hit_chance = bottom_hit_chance - ((distance - bottom_steps) * chance_per_step)

            return round(current_step_hit_chance, 2)

        @staticmethod
        def is_hit(hit_chance: Percentage) -> bool:
            hit_chance = percentage_to_float(hit_chance)
            return random.choices(
                [
                    True,
                    False
                ],
                [
                    hit_chance,
                    1 - hit_chance
                ]
            )[0]

        @classmethod
        def owner_moves_first(cls) -> bool:
            return cls.config.chance_first_move.owner >= random.random()

        @classmethod
        def user_buff(cls, games_played: int) -> float:
            _config = cls.config.user_buff
            buff = (
                    (games_played // _config.interval_of_games_played) *
                    _config.increase_hit_chance
            )
            if buff > _config.max_increase_hit_chance:
                return _config.max_increase_hit_chance
            return buff

    class ConfigSnowmanFallingChances:
        def __init__(self, height_increased: int):
            """
            Конфигурация шансов падения снеговика для игры ``/snowman``

            :param height_increased: на сколько сантиметров будет увеличен рост снеговика
            """
            self.height_increased = height_increased
            self.config = [
                SettingsConfigSnowman(
                    height_increased=1,
                    percentage_falling_chance='2%'
                ),
                SettingsConfigSnowman(
                    height_increased=2,
                    percentage_falling_chance='4%'
                ),
                SettingsConfigSnowman(
                    height_increased=3,
                    percentage_falling_chance='6%'
                ),
                SettingsConfigSnowman(
                    height_increased=4,
                    percentage_falling_chance='8%'
                ),
                SettingsConfigSnowman(
                    height_increased=5,
                    percentage_falling_chance='10%'
                ),
                SettingsConfigSnowman(
                    height_increased=6,
                    percentage_falling_chance='12%'
                ),
                SettingsConfigSnowman(
                    height_increased=7,
                    percentage_falling_chance='14%'
                ),
                SettingsConfigSnowman(
                    height_increased=8,
                    percentage_falling_chance='16%'
                ),
                SettingsConfigSnowman(
                    height_increased=9,
                    percentage_falling_chance='18%'
                ),
                SettingsConfigSnowman(
                    height_increased=10,
                    percentage_falling_chance='20%'
                ),
            ]

        @property
        def is_fall(self) -> bool:
            return random.random() <= self.ths_percentage_falling_chance

        @property
        def ths_percentage_falling_chance(self) -> float:
            return self.config[self.height_increased - 1].percentage_falling_chance


settings = Settings()
