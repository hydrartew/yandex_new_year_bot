import logging

import ydb
import ydb.iam

from configs import settings
from db.db_ydb.credentials import get_credentials
from schemas import ChatMemberUpdatedData

logger = logging.getLogger('db.ydb')

full_path: str = '{}/ynyb/chat_data/'.format(settings.YDB_DATABASE.removeprefix('/'))
table_name = 'chats'

credentials = get_credentials()


async def create_table() -> None:
    logger.info(f'Creating table {table_name} if not exists')

    async with ydb.aio.Driver(
        endpoint=settings.YDB_ENDPOINT,
        database=settings.YDB_DATABASE,
        credentials=credentials
    ) as driver:
        await driver.wait(fail_fast=True)

        async with ydb.aio.QuerySessionPool(driver) as _pool:
            try:
                await _pool.execute_with_retries(
                    """
                    PRAGMA TablePathPrefix("{}");
                    CREATE TABLE IF NOT EXISTS `{}` (
                        `chat_id` Int64 NOT NULL,
                        `type` Utf8 NOT NULL,
                        `title` Utf8,
                        `from_user_id` Uint64 NOT NULL,
                        `from_user_username` Utf8 NOT NULL,
                        `action` Utf8 NOT NULL,
                        `utc_dttm_action` Timestamp NOT NULL,
                        PRIMARY KEY (`chat_id`)
                    )
                    """.format(
                        full_path, table_name
                    )
                )
                logger.info(f'Table {table_name} created successfully')
            except Exception as e:
                logger.error(f'Error creating table {table_name}: {e}', exc_info=True)


async def upsert_chat_data(data: ChatMemberUpdatedData) -> None:
    logger.info('Upsert table {} with data: {}'.format(table_name, repr(data)))

    async with ydb.aio.Driver(
        endpoint=settings.YDB_ENDPOINT,
        database=settings.YDB_DATABASE,
        credentials=credentials
    ) as driver:
        await driver.wait(fail_fast=True)

        async with ydb.aio.QuerySessionPool(driver) as _pool:
            try:
                await _pool.execute_with_retries(
                    """
                    PRAGMA TablePathPrefix("{}");

                    DECLARE $chat_id AS Int64;
                    DECLARE $type AS Utf8;
                    DECLARE $title AS Optional<Utf8>;
                    DECLARE $from_user_id AS Uint64;
                    DECLARE $from_user_username AS Utf8;
                    DECLARE $action AS Utf8;
                    DECLARE $utc_dttm_action AS Timestamp;

                    UPSERT INTO `{}` (chat_id, type, title, from_user_id, from_user_username, action, utc_dttm_action)
                    VALUES ($chat_id, $type, $title, $from_user_id, $from_user_username, $action, $utc_dttm_action);
                    """.format(
                        full_path, table_name,
                    ),
                    {
                        "$chat_id": (data.chat_id, ydb.PrimitiveType.Int64),
                        "$type": (data.type, ydb.PrimitiveType.Utf8),
                        "$title": (data.title, ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                        "$from_user_id": (data.from_user_id, ydb.PrimitiveType.Uint64),
                        "$from_user_username": (data.from_user_username, ydb.PrimitiveType.Utf8),
                        "$action": (data.action, ydb.PrimitiveType.Utf8),
                        "$utc_dttm_action": (data.utc_dttm_action, ydb.PrimitiveType.Timestamp)
                    }
                )
                logger.info('Table {} updated successfully with data: {}'.format(table_name, repr(data)))
            except Exception as e:
                logger.error('Error while upsert table {} with data {}: {}'.format(
                    table_name, repr(data), e), exc_info=True)


async def main():
    await create_table()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
