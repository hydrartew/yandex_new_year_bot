import asyncio

from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentRuntimeCore

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


async def create_db_ydb_tables(flag: bool = False) -> None:
    if flag:
        await db_ydb.create_table_chat_data()
        await db_ydb.create_tables_predictions()


async def main() -> None:
    configure_logging()
    logger.info('Launching the bot')

    mw = I18nMiddleware(core=FluentRuntimeCore(path="locales/{locale}/LC_MESSAGES"))
    mw.setup(dispatcher=dp)

    dp.message.middleware(ThrottlingMiddleware())

    await create_db_ydb_tables()

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
