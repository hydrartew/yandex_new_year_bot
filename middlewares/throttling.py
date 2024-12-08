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
            'help': TTLCache(
                ttl=2, maxsize=10_000
            ),
            'night_king': TTLCache(
                ttl=60, maxsize=10_000
            ),
            'prediction': TTLCache(
                ttl=15, maxsize=10_000
            ),
            'quiz': TTLCache(
                ttl=10, maxsize=10_000
            ),
            'snow': TTLCache(
                ttl=1.5, maxsize=10_000
            ),
            'snow_duel': TTLCache(
                ttl=3, maxsize=10_000
            ),
            'snowman': TTLCache(
                ttl=1.5, maxsize=10_000
            ),
            'stats': TTLCache(
                ttl=30, maxsize=10_000
            )
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
                logger.debug(
                    'tg_user_id:{} blocked for {} seconds by the throttling_key "{}"'
                    .format(event.from_user.id, self.caches[throttling_key].ttl, throttling_key)
                )
                return
            self.caches[throttling_key][event.from_user.id] = None
        return await handler(event, data)
