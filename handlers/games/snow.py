from aiogram.filters import Command
from aiogram.types import Message

from configs import secret_box
from db import db_redis
from filters import GroupChat

from handlers import dp

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

    if secret_box.is_secret_box:
        number_snowballs = secret_box.number_snowballs
        await message.answer(
            text=f'@{message.from_user.username} бросил(а) подарок 🎁 в @{message.reply_to_message.from_user.username},'
                 f' в котором оказалось {number_snowballs} {get_snow_word(number_snowballs)} ❄️'
        )
    else:
        await message.answer(
            text=f'@{message.from_user.username} бросил(а) снежок ❄️ в @{message.reply_to_message.from_user.username}'
        )
    await db_redis.snow_plus_one(message.from_user.id, message.reply_to_message.from_user.id)


def get_snow_word(count: int) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return "снежок"
    elif 2 <= count % 10 <= 4 and not (12 <= count % 100 <= 14):
        return "снежка"
    else:
        return "снежков"
