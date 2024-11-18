import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from cachetools import TTLCache

logger = logging.getLogger('middleware')


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, time_limit: int = 5):
        self.limit = TTLCache(maxsize=10_000, ttl=time_limit)

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if event.chat.id in self.limit:
            logger.info(f'{event.chat} blocked {self.limit} seconds')
            return
        self.limit[event.chat.id] = None
        return await handler(event, data)
