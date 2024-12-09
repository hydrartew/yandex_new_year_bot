from aiogram.filters import Command
from aiogram.types import Message
from aiogram_i18n import I18nContext

from configs import settings
from db import db_ydb
from filters import GroupChat, IsSubscribed
from handlers import dp
from localization import Localization


@dp.message(Command('prediction'), GroupChat(), IsSubscribed(), flags={"throttling_key": "prediction"})
async def game_prediction(message: Message, i18n: I18nContext) -> None:
    localization = Localization(message, i18n)

    prediction = await db_ydb.get_prediction(message.from_user.id)

    if prediction.error_occurred:
        await message.reply(localization.get('prediction-error-occurred'))
        return

    if prediction.next_use_is_allowed_after is not None:
        await message.reply(
            localization.get(
                'prediction-next-use-is-allowed-after',
                PREDICTION_TIMEOUT_IN_HOURS=settings.PREDICTION_TIMEOUT_IN_HOURS,
                next_use_is_allowed_after=prediction.next_use_is_allowed_after
            )
        )
        return

    if prediction.no_suitable_predictions:
        await message.reply(localization.get('prediction-no-suitable'))
        return

    await message.answer(
        localization.get(
            'prediction',
            tg_username=message.from_user.username,
            prediction_text=prediction.text
        )
    )
