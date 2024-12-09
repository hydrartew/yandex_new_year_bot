from aiogram.filters import Command
from aiogram.types import Message
from aiogram_i18n import I18nContext

from configs import settings
from db.db_redis import update_snowman
from filters import GroupChat, IsSubscribed
from handlers import dp
from localization import Localization


@dp.message(Command('snowman'), GroupChat(), IsSubscribed(), flags={"throttling_key": "snowman"})
async def game_snowman(message: Message, i18n: I18nContext) -> None:
    localization = Localization(message, i18n)

    list_text = message.text.split()
    if len(list_text) != 2 or not list_text[1].isdigit() or int(list_text[1]) > 10 or int(list_text[1]) < 1:
        await message.reply(localization.get('snowman-bad-request'))
        return

    height_increased = int(list_text[1])
    snowman_data = await update_snowman(message.from_user.id, height_increased)

    snowman_fall = settings.ConfigSnowmanFallingChances(height_increased)

    # если снеговик упал и НЕ первый ход
    if snowman_fall.is_fall and (snowman_data.current - height_increased != 0):
        await message.answer(
            text=localization.get(
                'snowman-fall',
                tg_username=message.from_user.username,
                height_increased=height_increased,
                ths_percentage_falling_chance=f'{snowman_fall.ths_percentage_falling_chance:.0%}'
            )
        )
        await update_snowman(message.from_user.id, -1)
    else:
        await message.answer(
            text=localization.get(
                'snowman-increased',
                tg_username=message.from_user.username,
                height_increased=height_increased,
                current_height=snowman_data.current
            )
        )
