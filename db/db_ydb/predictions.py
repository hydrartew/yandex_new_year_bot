import json
import logging
import random
from datetime import datetime, timedelta

import ydb
import ydb.iam
from grpc import StatusCode
from grpc.aio import AioRpcError
from ydb import RetrySettings

from configs import settings
from db.db_ydb.credentials import credentials_manager
from schemas import RandomPrediction, DataUsedPredictions, DataMaxPredictionId, GetPrediction, PredictionStats

logger = logging.getLogger('db.ydb')

full_path: str = '{}/{}/predictions/'.format(settings.YDB_DATABASE.removesuffix('/'), settings.YDB_ROOT_DIR_NAME)

table_name_predictions = 'predictions'
table_name_used_predictions = 'used_predictions'


class DBPrediction:
    def __init__(self, tg_user_id: int):
        self.tg_user_id = tg_user_id

        global full_path, table_name_used_predictions, table_name_predictions

        self.full_path = full_path
        self.table_name_predictions = table_name_predictions
        self.table_name_used_predictions = table_name_used_predictions

    async def select_prediction(self, _pool: ydb.aio.QuerySessionPool, prediction_id: int) -> RandomPrediction | None:

        logger.info('Trying to get prediction:{} for tg_user_id:{}'.format(prediction_id, self.tg_user_id))

        try:
            result_sets = await _pool.execute_with_retries(
                """
                PRAGMA TablePathPrefix("{}");
                
                DECLARE $prediction_id AS Uint32;
                
                SELECT prediction_id, text FROM `{}` WHERE prediction_id == $prediction_id;
                """.format(
                    self.full_path, self.table_name_predictions
                ),
                {
                    '$prediction_id': (prediction_id, ydb.PrimitiveType.Uint32),
                }
            )

        except AioRpcError as err:
            if err.code() == StatusCode.RESOURCE_EXHAUSTED:
                logger.critical('YDB resource exhausted while select prediction:{}'.format(prediction_id))
            else:
                logger.error('Unknown AioRpcError while select prediction:{} {}'
                             .format(prediction_id, err), exc_info=True)

        except Exception as err:
            logger.error(f'Error while getting prediction for tg_user_id {self.tg_user_id}: {err}', exc_info=True)

        else:
            if len(result_sets[0].rows) != 0:
                random_prediction = result_sets[0].rows[0]
                logger.info('prediction_id:{} for tg_user_id:{} received successfully'.format(
                    random_prediction.prediction_id, self.tg_user_id
                ))
                return RandomPrediction.model_validate(random_prediction)

        logger.warning('No suitable predictions for tg_user_id:{}'.format(self.tg_user_id))
        return

    async def select_used_and_max_predictions(self, _pool: ydb.aio.QuerySessionPool
                                              ) -> tuple[DataUsedPredictions, DataMaxPredictionId] | None:
        global full_path

        logger.info(f'Trying to get used predictions for tg_user_id: {self.tg_user_id}')

        try:
            result_sets = await _pool.execute_with_retries(
                """
                PRAGMA TablePathPrefix("{}");
    
                DECLARE $tg_user_id AS Uint64;
    
                SELECT * FROM {} WHERE tg_user_id = $tg_user_id;
                
                SELECT MAX(prediction_id) as max_prediction_id FROM `{}`;
                """.format(
                    self.full_path, self.table_name_used_predictions, self.table_name_predictions
                ),
                {
                    '$tg_user_id': (self.tg_user_id, ydb.PrimitiveType.Uint64),
                }
            )

        except AioRpcError as err:
            if err.code() == StatusCode.RESOURCE_EXHAUSTED:
                logger.critical('YDB resource exhausted while getting used and max predictions for tg_user_id:{}'
                                .format(self.tg_user_id))
            else:
                logger.error('Unknown AioRpcError while getting used and max predictions for tg_user_id:{}: {}'
                             .format(self.tg_user_id, err), exc_info=True)
            return

        except Exception as err:
            logger.error('Error while getting used and max predictions for tg_user_id {}: {}'
                         .format(self.tg_user_id, err), exc_info=True)
            return

        if len(result_sets[0].rows) != 0:
            logger.info(f'Used predictions for tg_user_id {self.tg_user_id} received successfully')
            data_used_predictions = DataUsedPredictions.model_validate(result_sets[0].rows[0])
        else:
            data_used_predictions = DataUsedPredictions(tg_user_id=self.tg_user_id, dttm_last_usage=None)
            logger.info(f'No used predictions for tg_user_id {self.tg_user_id}')

        return data_used_predictions, DataMaxPredictionId.model_validate(result_sets[1].rows[0])

    async def upsert_data_used_predictions(self, pool: ydb.aio.QuerySessionPool,
                                           data_used_predictions: DataUsedPredictions) -> None:
        logger.info(f'Performing UPSERT into {self.table_name_used_predictions} for tg_user_id {self.tg_user_id}')

        try:
            await pool.execute_with_retries(
                f"""
                PRAGMA TablePathPrefix("{self.full_path}");

                DECLARE $tg_user_id AS Uint64;
                DECLARE $prediction_ids AS Json;
                DECLARE $usage_times AS Json;
                DECLARE $dttm_last_usage AS Timestamp;

                UPSERT INTO {self.table_name_used_predictions} 
                    (tg_user_id, prediction_ids, usage_times, dttm_last_usage)
                VALUES 
                    ($tg_user_id, $prediction_ids, $usage_times, $dttm_last_usage);
                """,
                {
                    "$tg_user_id": (data_used_predictions.tg_user_id, ydb.PrimitiveType.Uint64),
                    "$prediction_ids": (json.dumps(data_used_predictions.prediction_ids), ydb.PrimitiveType.Json),
                    "$usage_times": (json.dumps(data_used_predictions.usage_times), ydb.PrimitiveType.Json),
                    "$dttm_last_usage": (data_used_predictions.dttm_last_usage, ydb.PrimitiveType.Timestamp),
                }
            )
            logger.info(f'Data used predictions for tg_user_id {self.tg_user_id} has been updated successfully')
        except Exception as e:
            logger.error(f'Error UPSERT used_predictions: {data_used_predictions}: {e}', exc_info=True)

    async def get_stats(self, _pool: ydb.aio.QuerySessionPool) -> PredictionStats:

        logger.info('Trying to get number of predictions received for tg_user_id:{}'.format(self.tg_user_id))

        try:
            result_sets = await _pool.execute_with_retries(
                """
                PRAGMA TablePathPrefix("{}");

                DECLARE $tg_user_id AS Uint64;

                SELECT 
                    ListLength(Json::ConvertToList(prediction_ids)) AS received 
                FROM `{}` 
                WHERE tg_user_id == $tg_user_id;
                """.format(
                    self.full_path, self.table_name_used_predictions
                ),
                {
                    '$tg_user_id': (self.tg_user_id, ydb.PrimitiveType.Uint64),
                },
                retry_settings=RetrySettings(
                    max_retries=3
                )
            )
            logger.info('Prediction stats for tg_user_id:{} received successfully'.format(self.tg_user_id))

            received = 0
            if len(result_sets[0].rows) != 0:
                received = result_sets[0].rows[0].get('received')

            return PredictionStats(received=received)

        except AioRpcError as err:
            if err.code() == StatusCode.RESOURCE_EXHAUSTED:
                logger.error(
                    'YDB resource exhausted while getting prediction stats for tg_user_id:{}'.format(self.tg_user_id)
                )
            else:
                logger.error(
                    'Unknown AioRpcError while getting prediction stats for tg_user_id:{}'
                    .format(self.tg_user_id), exc_info=True
                )

        except Exception as err:
            logger.error(
                'Unknown error while getting prediction stats for tg_user_id:{}, err: {}'
                .format(self.tg_user_id, err), exc_info=True
            )

        return PredictionStats()


async def get_prediction(tg_user_id: int) -> GetPrediction:
    dbp = DBPrediction(tg_user_id)

    async with ydb.aio.Driver(
        endpoint=settings.YDB_ENDPOINT,
        database=settings.YDB_DATABASE,
        credentials=credentials_manager.get_credentials()
    ) as driver:
        try:
            await driver.wait()
        except Exception as e:
            logger.error('Error while connecting to YDB: {}'.format(e), exc_info=True)
            return GetPrediction(error_occurred=True)

        async with ydb.aio.QuerySessionPool(driver) as pool:
            tuple_predictions = await dbp.select_used_and_max_predictions(pool)

            if tuple_predictions is None:
                return GetPrediction(error_occurred=True)

            if tuple_predictions[0].dttm_last_usage is not None:
                time_diff = datetime.now() - tuple_predictions[0].dttm_last_usage
                if time_diff < timedelta(hours=settings.PREDICTION_TIMEOUT_IN_HOURS):
                    return GetPrediction(
                        next_use_is_allowed_after=timedelta(hours=settings.PREDICTION_TIMEOUT_IN_HOURS) - time_diff
                    )

            prediction_id = get_random_number(
                range_max=tuple_predictions[1].max_prediction_id,
                excluded_numbers=tuple_predictions[0].prediction_ids
            )

            if prediction_id is None:
                return GetPrediction(no_suitable_predictions=True)

            random_prediction = await dbp.select_prediction(pool, prediction_id)

            if random_prediction is None:
                return GetPrediction(no_suitable_predictions=True)

            tuple_predictions[0].prediction_ids.append(random_prediction.prediction_id)
            tuple_predictions[0].usage_times.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            tuple_predictions[0].dttm_last_usage = datetime.now()

            await dbp.upsert_data_used_predictions(pool, tuple_predictions[0])

            return GetPrediction(text=random_prediction.text)


async def get_prediction_stats(tg_user_id: int) -> PredictionStats:
    dbp = DBPrediction(tg_user_id)

    async with ydb.aio.Driver(
        endpoint=settings.YDB_ENDPOINT,
        database=settings.YDB_DATABASE,
        credentials=credentials_manager.get_credentials()
    ) as driver:
        try:
            await driver.wait(timeout=2, fail_fast=True)
        except Exception as e:
            logger.error('Error while connecting to YDB: {}'.format(e), exc_info=True)
            return PredictionStats()

        async with ydb.aio.QuerySessionPool(driver) as pool:
            return await dbp.get_stats(pool)


def get_random_number(range_max: int, excluded_numbers: list[int] | None = None) -> int | None:
    if excluded_numbers is None or len(excluded_numbers) == 0:
        return random.randint(0, range_max)

    _data = set(range(range_max + 1)) - set(excluded_numbers)
    return random.choice(list(_data)) if len(_data) > 0 else None


async def create_table_predictions(_pool: ydb.aio.QuerySessionPool) -> None:
    logger.info(f'Creating table {table_name_predictions} if not exists')

    try:
        await _pool.execute_with_retries(
            """
            PRAGMA TablePathPrefix("{}");
            CREATE TABLE IF NOT EXISTS `{}` (
                `prediction_id` Uint32 NOT NULL,
                `accepted` Bool NOT NULL,
                `author_staff_login` Utf8 NOT NULL,
                `dttm_created` Timestamp NOT NULL,
                `text` Utf8 NOT NULL,
                `issue_key` Utf8,
                PRIMARY KEY (`prediction_id`)
            )
            """.format(
                full_path, table_name_predictions
            )
        )
        logger.info(f'Table {table_name_predictions} created successfully')
    except Exception as e:
        logger.error(f'Error creating table {table_name_predictions}: {e}', exc_info=True)
        raise


async def create_table_used_predictions(_pool: ydb.aio.QuerySessionPool) -> None:
    logger.info(f'Creating table {table_name_used_predictions} if not exists')
    try:
        await _pool.execute_with_retries(
            """
            PRAGMA TablePathPrefix("{}");
            CREATE TABLE IF NOT EXISTS `{}` (
                `tg_user_id` Uint64 NOT NULL,
                `prediction_ids` Json NOT NULL,
                `usage_times` Json NOT NULL,
                `dttm_last_usage` Timestamp NOT NULL,
                PRIMARY KEY (`tg_user_id`)
            )
            """.format(
                full_path, table_name_used_predictions
            )
        )
        logger.info(f'Table {table_name_used_predictions} created successfully')
    except Exception as e:
        logger.error(f'Error creating table {table_name_used_predictions}: {e}', exc_info=True)
        raise


async def create_tables_predictions() -> None:
    async with ydb.aio.Driver(
            endpoint=settings.YDB_ENDPOINT,
            database=settings.YDB_DATABASE,
            credentials=credentials_manager.get_credentials()
    ) as driver:
        await driver.wait(timeout=7, fail_fast=True)

        async with ydb.aio.QuerySessionPool(driver) as pool:
            await create_table_predictions(pool)
            await create_table_used_predictions(pool)
