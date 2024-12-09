import logging

from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log

import ydb
import ydb.iam
from grpc import StatusCode
from grpc.aio import AioRpcError

from configs import settings
from db.db_ydb.credentials import credentials_manager

from schemas import ChatMemberUpdatedData

logger = logging.getLogger('db.ydb')

full_path: str = '{}/ynyb/chat_data/'.format(settings.YDB_DATABASE.removeprefix('/'))
table_name = 'chats'


async def create_table_chat_data() -> None:
    logger.info(f'Creating table {table_name} if not exists')

    async with ydb.aio.Driver(
        endpoint=settings.YDB_ENDPOINT,
        database=settings.YDB_DATABASE,
        credentials=credentials_manager.get_credentials()
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
                        `from_user_language_code` Utf8 NOT NULL,
                        `chat_member_status` Utf8 NOT NULL,
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
                raise


@retry(
    stop=stop_after_attempt(7),
    wait=wait_exponential(
        multiplier=2,
        min=5,
        max=60
    ),
    before_sleep=before_sleep_log(logger, logging.INFO)
)
async def upsert_chat_data(data: ChatMemberUpdatedData) -> None:
    logger.info('Upsert table `{}` with data: {}'.format(table_name, repr(data)))

    async with ydb.aio.Driver(
        endpoint=settings.YDB_ENDPOINT,
        database=settings.YDB_DATABASE,
        credentials=credentials_manager.get_credentials()
    ) as driver:
        try:
            await driver.wait()
        except Exception as e:
            logger.error('Error while connecting to YDB: {}'.format(e), exc_info=True)
            raise
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
                    DECLARE $from_user_language_code AS Utf8;
                    DECLARE $chat_member_status AS Utf8;
                    DECLARE $utc_dttm_action AS Timestamp;

                    UPSERT INTO `{}` (
                        chat_id, 
                        type, 
                        title, 
                        from_user_id, 
                        from_user_username, 
                        from_user_language_code,
                        chat_member_status,
                        utc_dttm_action
                    )
                    VALUES (
                        $chat_id, 
                        $type, 
                        $title, 
                        $from_user_id, 
                        $from_user_username,
                        $from_user_language_code,
                        $chat_member_status, 
                        $utc_dttm_action
                    );
                    """.format(
                        full_path, table_name,
                    ),
                    {
                        "$chat_id": (data.chat_id, ydb.PrimitiveType.Int64),
                        "$type": (data.type, ydb.PrimitiveType.Utf8),
                        "$title": (data.title, ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                        "$from_user_id": (data.from_user_id, ydb.PrimitiveType.Uint64),
                        "$from_user_username": (data.from_user_username, ydb.PrimitiveType.Utf8),
                        "$from_user_language_code": (data.from_user_language_code, ydb.PrimitiveType.Utf8),
                        "$chat_member_status": (data.chat_member_status, ydb.PrimitiveType.Utf8),
                        "$utc_dttm_action": (data.utc_dttm_action, ydb.PrimitiveType.Timestamp)
                    }
                )
                logger.info('Table `{}` updated successfully for chat_id:{}'.format(table_name, data.chat_id))

            except AioRpcError as err:
                if err.code() == StatusCode.RESOURCE_EXHAUSTED:
                    logger.error(
                        'YDB resource exhausted while UPSERT `{}` with chat_data:{}'
                        .format(table_name, repr(data.chat_id))
                    )
                else:
                    logger.error(
                        'Unknown AioRpcError while UPSERT `{}` with chat_data:{} {}'
                        .format(table_name, repr(data), err), exc_info=True
                    )
                raise
            except Exception as e:
                logger.error(
                    'Error while upsert UPSERT `{}` with data {}: {}'.format(table_name, repr(data), e), exc_info=True
                )
                raise
