from datetime import datetime

from pydantic import BaseModel


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
