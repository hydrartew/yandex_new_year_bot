from aiogram.filters import Command
from aiogram.types import Message
from aiogram_i18n import I18nContext

from configs import settings
from db.db_redis import get_user_stats
from filters import GroupChat, IsSubscribed
from handlers import dp
from localization import Localization


@dp.message(Command('night_king'), GroupChat(), IsSubscribed(), flags={"throttling_key": "night_king"})
async def night_king(message: Message, i18n: I18nContext) -> None:
    localization = Localization(message, i18n)

    user_stats = await get_user_stats(message.from_user.id)

    if user_stats.losses < settings.NIGHT_KING_LOSS_THRESHOLD_TO_GET_ACHIEVEMENT:
        await message.reply(localization.get('night-king-unavailable'))

    else:
        # TODO: добавить выдачу ачивки
        await message.reply(localization.get('night-king-unblocked'))
