import logging

from aiogram.filters import Command
from aiogram.types import Message

from configs import secret_box
from db import db_redis
from filters import GroupChat

from handlers import dp

logger = logging.getLogger('handlers')

flags = {"throttling_key": "snow"}


@dp.message(Command('snow'), GroupChat(), flags=flags)
async def game_snow(message: Message) -> None:
    # если сообщение без reply
    if message.reply_to_message is None:
        await message.answer(f'@{message.from_user.username} бросил(а) снежок ❄️ в воздух')
        return

    # если reply на сообщение бота
    if message.reply_to_message.from_user.is_bot:
        await message.answer(
            text=f'@{message.from_user.username} бросил(а) снежок ❄️ в @{message.reply_to_message.from_user.username}, '
                 f'но не попал(а)',
        )
        return

    # если reply на свое сообщение
    if message.from_user.username == message.reply_to_message.from_user.username:
        await message.answer(
            text=f'@{message.from_user.username} бросил(а) снежок ❄️ в себя',
        )
        return

    logger.info('/snow tg_user_id:{} reply to tg_user_id:{} in chat_id:{}'.format(
        message.from_user.id, message.reply_to_message.from_user.id, message.chat.id))

    if secret_box.is_secret_box:
        number_snowballs = secret_box.number_snowballs
        await message.answer(
            text=f'@{message.from_user.username} получил(а) подарок 🎁, '
                 f'в котором {get_snow_phrase(number_snowballs)} ❄️'
        )
        await db_redis.snow_increase(message.from_user.id, from_tg_user_id_amount=number_snowballs)

    else:
        await message.answer(
            text=f'@{message.from_user.username} бросил(а) снежок ❄️ в @{message.reply_to_message.from_user.username}'
        )
        await db_redis.snow_increase(message.from_user.id, to_tg_user_id=message.reply_to_message.from_user.id)


def get_snow_phrase(c: int) -> str:
    if c % 10 == 1 and c % 100 != 11:
        return f'оказался {c} снежок'
    elif 2 <= c % 10 <= 4 and not (12 <= c % 100 <= 14):
        return f'оказалось {c} снежка'
    else:
        return f'оказалось {c} снежков'
