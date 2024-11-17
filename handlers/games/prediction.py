from aiogram.filters import Command
from aiogram.types import Message

from db import db_ydb
from handlers import dp


@dp.message(Command('prediction'))
async def game_prediction(message: Message) -> None:
    # TODO: добавить проверку на последнее время использования
    prediction_text = await db_ydb.get_prediction(message.from_user.id)
    await message.answer(f'Предсказание 🔮 для @{message.from_user.username}:\n\n' + prediction_text)
