from datetime import datetime, timedelta
from enum import Enum
from typing import Literal, Annotated

from aiogram.enums import ChatMemberStatus
from pydantic import BaseModel, field_validator, computed_field, AfterValidator


def percentage_to_float(v: str | float) -> float:
    if isinstance(v, str):
        v = float(v.strip('%')) / 100
    if not (0 <= v <= 1):
        raise ValueError('Percentage chance must be between 0.00 and 1.00')
    return v


Percentage = Annotated[str | float, AfterValidator(percentage_to_float)]


class RandomPrediction(BaseModel):
    prediction_id: int
    text: str


class DataUsedPredictions(BaseModel):
    tg_user_id: int
    prediction_ids: list[int] = []
    usage_times: list[str] = []
    dttm_last_usage: datetime = datetime.now()


class DataMaxPredictionId(BaseModel):
    max_prediction_id: int


class GetPrediction(BaseModel):
    error_occurred: bool = False
    next_use_is_allowed_after: timedelta | None = None
    no_suitable_predictions: bool = False
    text: str | None = None

    @field_validator('next_use_is_allowed_after')
    @classmethod
    def reformat_next_use_is_allowed_after(cls, v: timedelta | None) -> str | None:
        if isinstance(v, timedelta):
            hours, remainder = divmod(v.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


class PredictionStats(BaseModel):
    received: int | None = None

    def model_post_init(self, __context):
        self.received = 'N/A' if not self.received else self.received


class SnowRedisData(BaseModel):
    throw: int = 0
    get: int = 0


class SnowmanRedisData(BaseModel):
    all_attempts: int = 0
    current: int = 0
    maximum: int = 0


class SnowDuelUserStats(BaseModel):
    wins: int = 0
    losses: int = 0

    @computed_field
    @property
    def amount(self) -> int:
        return self.wins + self.losses

    @computed_field
    @property
    def wins_percentage(self) -> str:
        if self.amount == 0:
            return '0%'
        percentage = (self.wins / self.amount) * 100
        return f"{percentage:.2f}%"

    @computed_field
    @property
    def losses_percentage(self) -> str:
        if self.amount == 0:
            return '0%'
        percentage = (self.losses / self.amount) * 100
        return f"{percentage:.2f}%"


class SnowDuelUser(BaseModel):
    tg_user_id: int
    tg_username: str
    hit_chance: Percentage
    points: int = 0
    moves: int = 0
    dttm_last_move: datetime | None = None

    @field_validator('tg_username')
    @classmethod
    def validate_tg_username(cls, v: str) -> str:
        return v.removeprefix('@')


class WhoMoves(Enum):
    owner = 'owner'
    opponent = 'opponent'


class SnowDuelRoom(BaseModel):
    game_status: Literal['created', 'in_progress', 'finished', 'cancelled']
    owner: SnowDuelUser
    opponent: SnowDuelUser | None = None
    who_moves: WhoMoves | None = None
    current_round: int = 1
    distance: int
    dttm_created: datetime


class MakeMove(BaseModel):
    user_in_room: bool = True
    is_current_user_move: bool = True
    room_exists: bool = True
    snow_duel_data: SnowDuelRoom | None = None
    is_hit: bool = False


class AddOpponentToRoom(BaseModel):
    room_exists: bool = True
    room_already_has_opponent: bool = False
    user_is_owner_already_in_room: bool = False
    snow_duel_data: SnowDuelRoom | None = None


class TgUsernamesWhoThrowsAndWhoGets(BaseModel):
    throw: str
    get: str


class CancelGame(BaseModel):
    another_user_id: int | None = None
    snow_duel_data: SnowDuelRoom


class ChatMemberUpdatedData(BaseModel):
    chat_id: int
    type: str
    title: str | None
    from_user_id: int
    from_user_username: str
    chat_member_status: ChatMemberStatus
    utc_dttm_action: datetime


class NumberSnowballs(BaseModel):
    from_: int
    to: int


class SettingsConfigSnow(BaseModel):
    percentage_chance: Percentage
    number_snowballs: NumberSnowballs


class BottomBound(BaseModel):
    steps: int
    hit_chance: Percentage


class UpperBound(BottomBound):
    ...


class Distance(BaseModel):
    bottom_bound: BottomBound
    upper_bound: UpperBound


class ChanceFirstMove(BaseModel):
    owner: Percentage

    @computed_field
    @property
    def opponent(self) -> float:
        return 1 - self.owner


class UserBuff(BaseModel):
    interval_of_games_played: int
    increase_hit_chance: Percentage
    max_increase_hit_chance: Percentage


class SettingsConfigSnowDuel(BaseModel):
    distance: Distance
    chance_first_move: ChanceFirstMove
    user_buff: UserBuff


class SettingsConfigSnowman(BaseModel):
    height_increased: int
    percentage_falling_chance: Percentage
