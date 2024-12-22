import logging

from aiogram.filters import Command
from aiogram.types import Message
from aiogram_i18n import I18nContext

from configs import settings
from db.db_redis import get_user_stats, set_night_king_flag
from filters import GroupChat, IsSubscribed
from handlers import dp
from localization import Localization

logger = logging.getLogger(__name__)


@dp.message(Command('night_king'), GroupChat(), IsSubscribed(), flags={"throttling_key": "night_king"})
async def night_king(message: Message, i18n: I18nContext) -> None:
    """Скрытая команда для получения ачивки"""
    localization = Localization(message, i18n)

    logger.info('/night_king tg_user_id:{}, start of command processing'.format(message.from_user.id))

    user_stats = await get_user_stats(message.from_user.id)

    if user_stats.losses < settings.NIGHT_KING_LOSS_THRESHOLD_TO_GET_ACHIEVEMENT:
        logger.info(
            'The achievement is not available yet for tg_user_id:{}, as the threshold:{} has not been crossed.'
            .format(message.from_user.id, user_stats.losses)
        )
        await message.reply(localization.get('night-king-unavailable'))

    else:
        flag = await set_night_king_flag(message.from_user.id)

        if flag.already_exists:
            await message.reply(localization.get('night-king-already-given'))
        else:
            await message.reply(localization.get('night-king-unblocked'))

    logger.info('/night_king tg_user_id:{}, end of command processing'.format(message.from_user.id))
