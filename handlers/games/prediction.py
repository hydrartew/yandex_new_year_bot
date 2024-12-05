from aiogram.filters import Command
from aiogram.types import Message

from db import db_ydb
from filters import GroupChat
from handlers import dp

flags = {"throttling_key": "prediction"}


@dp.message(Command('prediction'), GroupChat(), flags=flags)
async def game_prediction(message: Message) -> None:
    prediction = await db_ydb.get_prediction(message.from_user.id)

    if prediction.error_occurred:
        await message.reply('Произошла ошибка при получении предсказания 😳. Попробуй получить предсказание позже')
        return

    if prediction.next_use_is_allowed_after is not None:
        await message.reply(
            'Предсказание 🔮 можно получить 1 раз в 12ч. Следующее предсказание будет доступно через {}'.format(
                prediction.next_use_is_allowed_after
            ))
        return

    if prediction.no_suitable_predictions:
        await message.reply('Предсказания для тебя закончились 😳. Попробуй получить предсказание позже')
        return

    await message.answer(f'Предсказание 🔮 для @{message.from_user.username}:\n\n' + prediction.text)
