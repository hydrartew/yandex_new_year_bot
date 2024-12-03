import asyncio

from handlers import dp

import logging.config

from loader import bot
from middlewares import ThrottlingMiddleware


async def main() -> None:
    logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
    logging.getLogger('db.ydb').propagate = False
    logging.getLogger('middleware').propagate = False
    logging.getLogger('db.redis').propagate = False
    logging.getLogger('handlers').propagate = False
    logging.getLogger('aiogram.dispatcher').propagate = False
    logging.getLogger('ydb').setLevel(logging.WARNING)

    dp.message.middleware(ThrottlingMiddleware())

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
