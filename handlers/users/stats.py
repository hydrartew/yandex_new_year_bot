from aiogram.filters import Command
from aiogram.types import Message

from db import db_redis

from loader import dp


@dp.message(Command('stats', 'profile'))
async def my_stats(message: Message) -> None:
    # TODO: select stats from DB

    snow_stats = await db_redis.get_snow_stats(message.from_user.id)
    snowman_stats = await db_redis.get_snowman(message.from_user.id)
    await message.reply(
        f'📊 Статистика @{message.from_user.username}\n\n'
        f'❄️ Снежный денек:\n'
        f'- брошено снежков: {snow_stats.throw}\n'
        f'- получено снежков: {snow_stats.get}\n\n'
        f'❄️🔫 Снежная дуэль:\n'
        f'- выиграно: C\n'
        f'- проиграно: D\n\n'
        f'☃️ Снеговичок:\n'
        f'- текущий: {snowman_stats.current} см\n'
        f'- самый высокий: {snowman_stats.maximum} см\n'
        f'- попыток слепить: {snowman_stats.all_attempts} шт\n\n'
        f'🔮 Предсказания:\n'
        f'- написано: G\n'
        f'- использовано: H\n\n'
    )
