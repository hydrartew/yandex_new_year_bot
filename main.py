import asyncio

from db import db_ydb
from handlers import dp

import logging.config

from loader import bot
from middlewares import ThrottlingMiddleware

logger = logging.getLogger('handlers')


def configure_logging():
    logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
    logging.getLogger('ydb').setLevel(logging.WARNING)
    for module in ('db.ydb', 'middleware', 'db.redis', 'handlers', 'aiogram.dispatcher'):
        logging.getLogger(module).propagate = False


async def main() -> None:
    configure_logging()
    logger.info('Launching the bot')

    dp.message.middleware(ThrottlingMiddleware())

    # if not exists
    # await db_ydb.create_table_chat_data()
    # await db_ydb.create_tables_predictions()

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
