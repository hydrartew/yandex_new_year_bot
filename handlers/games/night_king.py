from aiogram.filters import Command
from aiogram.types import Message

from configs import settings
from db.db_redis import get_user_stats
from filters import GroupChat, IsSubscribed
from handlers import dp


@dp.message(Command('night_king'), GroupChat(), IsSubscribed(), flags={"throttling_key": "night_king"})
async def night_king(message: Message) -> None:
    user_stats = await get_user_stats(message.from_user.id)
    if user_stats.losses < settings.NIGHT_KING_LOSS_THRESHOLD_TO_GET_ACHIEVEMENT:
        await message.reply('Пока недоступно, попробуй позже')
        return

    # TODO: добавить выдачу ачивки

    await message.reply(
        'Ночной король 👑 разблокирован!\n'
        'Ачивка отобразится на Стаффе в течение нескольких минут (в редких случаях - в течение часа)'
    )
