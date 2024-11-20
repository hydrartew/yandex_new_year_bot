import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from cachetools import TTLCache

logger = logging.getLogger('middleware')


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, throttle_time_prediction: float = 10, throttle_time_snow: float = 1.5):
        self.caches = {
            'prediction': TTLCache(maxsize=10_000, ttl=throttle_time_prediction),
            'snow': TTLCache(maxsize=10_000, ttl=throttle_time_snow),
        }

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        throttling_key = get_flag(data, "throttling_key")
        if throttling_key is not None and throttling_key in self.caches:
            if event.from_user.id in self.caches[throttling_key]:
                logger.info(f'tg_user_id:{event.from_user.id} blocked for {self.caches[throttling_key].ttl} seconds '
                            f'by the throttling_key "{throttling_key}"')
                return
            else:
                self.caches[throttling_key][event.from_user.id] = None
        return await handler(event, data)
