from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, field_validator, computed_field


class RandomPrediction(BaseModel):
    prediction_id: int
    text: str


class DataUsedPredictions(BaseModel):
    tg_user_id: int
    prediction_ids: list[int] = []
    usage_times: list[str] = []
    dttm_last_usage: datetime = datetime.now()


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
    hit_chance: float
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
