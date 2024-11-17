import random

from aiogram.filters import Command
from aiogram.types import Message

from handlers import dp


@dp.message(Command('prediction'))
async def game_prediction(message: Message) -> None:
    # TODO: select random prediction from DB
    prediction = f'Предсказание или пожелание с каким-то текстом #{random.randint(1, 1000)}'
    await message.answer(f'Предсказание 🔮 для @{message.from_user.username}:\n\n' + prediction)
