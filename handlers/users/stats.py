from aiogram.filters import Command
from aiogram.types import Message

from db import db_redis

from loader import dp


@dp.message(Command('stats', 'profile'))
async def my_stats(message: Message) -> None:
    # TODO: select stats from DB

    snow_stats = await db_redis.get_snow_stats(message.from_user.id)
    await message.reply(
        f'📊 Статистика @{message.from_user.username}\n\n'
        f'❄️ Снежный денек:\n'
        f'- брошено снежков: {snow_stats[0]}\n'
        f'- получено снежок: {snow_stats[1]}\n\n'
        f'❄️🔫 Снежная дуэль:\n'
        f'- выиграно: C\n'
        f'- проиграно: D\n\n'
        f'☃️ Снеговичок:\n'
        f'- попыток слепить: E\n'
        f'- самый высокий: F\n\n'
        f'🔮 Предсказания:\n'
        f'- написано: G\n'
        f'- использовано: H\n\n'
    )
