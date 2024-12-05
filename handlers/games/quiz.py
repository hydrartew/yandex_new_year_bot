from aiogram.filters import Command
from aiogram.types import Message

from filters import GroupChat
from loader import dp


@dp.message(Command('quiz'), GroupChat(), flags={"throttling_key": "quiz"})
async def game_quiz(message: Message) -> None:
    await message.reply(
        'Игра пока недоступна, следи за обновлениями в телеграм канале '
        '<a href="https://nda.ya.ru/t/8Ve9IRKc79adW7">YNYB News</a>'
    )
