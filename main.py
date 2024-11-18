import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config_data import settings
from handlers import dp

import logging.config


async def main() -> None:
    logging.config.fileConfig('logging.ini')
    logging.getLogger('db.ydb').propagate = False

    bot = Bot(settings.TELEGRAM_BOT_TOKEN.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # dp.message.middleware(ThrottlingMiddleware(config.throttle_time_spin, config.throttle_time_other))

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
