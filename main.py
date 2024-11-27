import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from configs import settings
from handlers import dp

import logging.config

from middlewares import ThrottlingMiddleware


async def main() -> None:
    logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
    logging.getLogger('db.ydb').propagate = False
    logging.getLogger('middleware').propagate = False
    logging.getLogger('db.redis').propagate = False
    logging.getLogger('handlers').propagate = False

    bot = Bot(settings.TELEGRAM_BOT_TOKEN.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.message.middleware(ThrottlingMiddleware())

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
