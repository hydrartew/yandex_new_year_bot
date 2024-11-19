import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message
from cachetools import TTLCache
from icecream import ic

logger = logging.getLogger('middleware')


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, time_limit: int = 2):
        self.limit = TTLCache(maxsize=10_000, ttl=time_limit)

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        # ic(self.limit)
        if event.from_user.id in self.limit:
            logger.info(f'tg_user_id:{event.from_user.id} blocked {self.limit.ttl} seconds')
            return
        self.limit[event.from_user.id] = None
        return await handler(event, data)
