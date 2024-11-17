from aiogram.filters import Command
from aiogram.types import Message

from handlers import dp


@dp.message(Command('snow'))
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

    await message.answer(
        text=f'@{message.from_user.username} бросил(а) снежок ❄️ в @{message.reply_to_message.from_user.username}'
    )

    # TODO: счетчик снежков для user`a += 1
