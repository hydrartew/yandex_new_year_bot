import json
import logging
import random
from datetime import datetime

import ydb
import ydb.iam
from grpc import StatusCode
from grpc.aio import AioRpcError

from configs import settings
from db.db_ydb.credentials import credentials_manager
from schemas import RandomPrediction, DataUsedPredictions, DataMaxPredictionId

logger = logging.getLogger('db.ydb')

full_path: str = '{}/ynyb/predictions/'.format(settings.YDB_DATABASE.removeprefix('/'))

table_name_predictions = 'predictions'
table_name_used_predictions = 'used_predictions'


def __create_table_used_predictions() -> None:
    global full_path, table_name_predictions, table_name_used_predictions
    logger.info(f'Creating table {table_name_used_predictions} if not exists')

    with ydb.Driver(
            endpoint=settings.YDB_ENDPOINT,
            database=settings.YDB_DATABASE,
            credentials=credentials_manager.get_credentials()
    ) as driver:
        driver.wait(timeout=5, fail_fast=True)
        with ydb.QuerySessionPool(driver) as _pool:
            try:
                _pool.execute_with_retries(
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
            data_used_predictions = DataUsedPredictions(tg_user_id=self.tg_user_id)
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


async def get_prediction(tg_user_id: int) -> str:
    dbp = DBPrediction(tg_user_id)

    async with ydb.aio.Driver(
            endpoint=settings.YDB_ENDPOINT,
            database=settings.YDB_DATABASE,
            credentials=credentials_manager.get_credentials()
    ) as driver:
        await driver.wait(fail_fast=True)

        async with ydb.aio.QuerySessionPool(driver) as pool:
            tuple_predictions = await dbp.select_used_and_max_predictions(pool)

            if tuple_predictions is None:
                return 'No suitable predictions'

            random_prediction = await dbp.select_prediction(pool, get_random_number(
                range_max=tuple_predictions[1].max_prediction_id,
                excluded_numbers=tuple_predictions[0].prediction_ids
            ))

            if random_prediction is None:
                return 'No suitable predictions'

            tuple_predictions[0].prediction_ids.append(random_prediction.prediction_id)
            tuple_predictions[0].usage_times.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            tuple_predictions[0].dttm_last_usage = datetime.now()

            await dbp.upsert_data_used_predictions(pool, tuple_predictions[0])

            return random_prediction.text


def get_random_number(range_max: int, excluded_numbers: list[int] | None = None):
    while True:
        random_number = random.randint(0, range_max)
        if excluded_numbers is None or random_number not in excluded_numbers:
            return random_number
