import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from cachetools import TTLCache

logger = logging.getLogger('middleware')


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self):
        self.caches = {
            'prediction': TTLCache(
                maxsize=10_000,
                ttl=10
            ),
            'snow': TTLCache(
                maxsize=10_000,
                ttl=1.5
            ),
            'stats': TTLCache(
                maxsize=10_000,
                ttl=30
            ),
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
                logger.info('tg_user_id:{} blocked for {} seconds by the throttling_key "{}"'.format(
                    event.from_user.id, self.caches[throttling_key].ttl, throttling_key))
                return
            self.caches[throttling_key][event.from_user.id] = None
        return await handler(event, data)
