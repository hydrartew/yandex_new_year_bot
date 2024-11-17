import json
import logging.config
from datetime import datetime

import ydb
import ydb.iam

from config_data import settings, credentials
from schemas import RandomPrediction, DataUsedPredictions

logging.config.fileConfig(settings.BASE_DIR + '/logging.ini')
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
            credentials=credentials
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
            except Exception as e:
                logger.error(f'Error creating table {table_name_used_predictions}: {e}', exc_info=True)


class DBPrediction:
    def __init__(self, tg_user_id: int):
        self.tg_user_id = tg_user_id

        global full_path, table_name_used_predictions, table_name_predictions

        self.full_path = full_path
        self.table_name_predictions = table_name_predictions
        self.table_name_used_predictions = table_name_used_predictions

    async def select_random_prediction(self, _pool: ydb.aio.QuerySessionPool,
                                       exclude_prediction_ids: list[int] | None) -> RandomPrediction | None:

        if exclude_prediction_ids is None:
            exclude_prediction_ids = []

        logger.info(f'Trying to get random prediction for tg_user_id: {self.tg_user_id}')

        try:
            result_sets = await _pool.execute_with_retries(
                """
                PRAGMA TablePathPrefix("{}");
                
                DECLARE $exclude_prediction_ids AS List<Uint32>;
                DECLARE $exclude_tg_user_id AS Uint64;
                
                SELECT
                    prediction_id,
                    text
                FROM {}
                WHERE 
                    author_tg_user_id != $exclude_tg_user_id 
                    AND prediction_id NOT IN $exclude_prediction_ids
                ORDER BY dttm_last_usage DESC
                LIMIT 1;
                """.format(
                    self.full_path, self.table_name_predictions
                ),
                {
                    '$exclude_tg_user_id': (self.tg_user_id, ydb.PrimitiveType.Uint64),
                    '$exclude_prediction_ids': (exclude_prediction_ids, ydb.ListType(ydb.PrimitiveType.Uint32))
                }
            )
        except Exception as err:
            logger.error(f'Error while getting prediction for tg_user_id {self.tg_user_id}: {err}', exc_info=True)
        else:
            if len(result_sets[0].rows) != 0:
                random_prediction = result_sets[0].rows[0]
                logger.info(f'Prediction for tg_user_id {self.tg_user_id} received successfully: {random_prediction}')
                return RandomPrediction.model_validate(random_prediction)

        logger.warning(f'No suitable predictions for tg_user_id {self.tg_user_id}')
        return

    async def select_used_predictions(self, _pool: ydb.aio.QuerySessionPool) -> DataUsedPredictions | None:
        global full_path

        logger.info(f'Trying to get used predictions for tg_user_id: {self.tg_user_id}')

        try:
            result_sets = await _pool.execute_with_retries(
                """
                PRAGMA TablePathPrefix("{}");
    
                DECLARE $tg_user_id AS Uint64;
    
                SELECT * 
                FROM {}
                WHERE tg_user_id = $tg_user_id;
                """.format(
                    self.full_path, self.table_name_used_predictions
                ),
                {
                    '$tg_user_id': (self.tg_user_id, ydb.PrimitiveType.Uint64),
                }
            )
        except Exception as err:
            logger.error(f'Error while getting used predictions for tg_user_id {self.tg_user_id}: {err}', exc_info=True)
            return

        if len(result_sets[0].rows) != 0:
            logger.info(f'Used predictions for tg_user_id {self.tg_user_id} received successfully')
            data_used_predictions = DataUsedPredictions.model_validate(result_sets[0].rows[0])
        else:
            data_used_predictions = DataUsedPredictions(tg_user_id=self.tg_user_id)
            logger.info(f'No used predictions for tg_user_id {self.tg_user_id}')

        return data_used_predictions

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
            credentials=credentials
    ) as driver:
        await driver.wait(timeout=5, fail_fast=True)

        async with ydb.aio.QuerySessionPool(driver) as pool:
            used_predictions = await dbp.select_used_predictions(pool)

            exclude_prediction_ids = None
            if used_predictions is not None:  # None, если произошла ошибка в получении использованных предсказаний
                exclude_prediction_ids = used_predictions.prediction_ids

            random_prediction = await dbp.select_random_prediction(pool, exclude_prediction_ids)

            if random_prediction is None:
                return 'No suitable predictions'

            used_predictions.prediction_ids.append(random_prediction.prediction_id)
            used_predictions.usage_times.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            used_predictions.dttm_last_usage = datetime.now()

            await dbp.upsert_data_used_predictions(pool, used_predictions)

            return random_prediction.text
