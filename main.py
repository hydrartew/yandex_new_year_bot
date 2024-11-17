import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config_data import settings
from handlers import dp

import logging.config


logging.config.fileConfig('logging.ini')
logging.getLogger('db.ydb').propagate = False


async def main() -> None:
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
