from aiogram.filters import Command
from aiogram.types import Message

from configs import snow_duel_config
from db import db_redis

from loader import dp


@dp.message(Command('stats', 'profile'), flags={"throttling_key": "stats"})
async def my_stats(message: Message) -> None:
    # TODO: +predictions

    stats = await db_redis.get_stats(message.from_user.id)

    await message.reply(
        f'📊 Статистика @{message.from_user.username}\n\n'
        f'❄️ Снежный денек:\n'
        f'- брошено снежков: {stats[0].throw}\n'
        f'- получено снежков: {stats[0].get}\n\n'
        f'❄️🔫 Снежная дуэль:\n'
        f'- выиграно: {stats[2].wins} ({stats[2].wins_percentage})\n'
        f'- проиграно: {stats[2].losses} ({stats[2].losses_percentage})\n'
        f'- бафф: +{snow_duel_config.user_buff(stats[2].amount):.2f}%\n\n'
        f'☃️ Снеговичок:\n'
        f'- текущий: {stats[1].current} см\n'
        f'- самый высокий: {stats[1].maximum} см\n'
        f'- попыток слепить: {stats[1].all_attempts} шт\n\n'
        f'🔮 Предсказания:\n'
        f'- написано: N/A\n'
        f'- получено: N/A\n\n'
    )
