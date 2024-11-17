from aiogram.filters import Command
from aiogram.types import Message

from loader import dp


@dp.message(Command('quiz'))
async def game_quiz(message: Message) -> None:
    # TODO: игра пока что на стадии идеи
    await message.reply(f'Игра пока недоступна, следи за обновлениями в телеграм канале "ссылка на тг канал"')
