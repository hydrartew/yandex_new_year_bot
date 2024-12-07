from aiogram.filters import Command
from aiogram.types import Message

from configs import snow_duel_config
from db import db_redis, db_ydb

from loader import dp


@dp.message(Command('stats', 'profile'), flags={"throttling_key": "stats"})
async def my_stats(message: Message) -> None:

    game_stats = await db_redis.get_stats(message.from_user.id)
    prediction_stats = await db_ydb.get_prediction_stats(message.from_user.id)

    await message.reply(
        f'📊 Статистика @{message.from_user.username}\n\n'
        f'❄️ Снежный денек:\n'
        f'- брошено снежков: {game_stats[0].throw}\n'
        f'- получено снежков: {game_stats[0].get}\n\n'
        f'❄️🔫 Снежная дуэль:\n'
        f'- выиграно: {game_stats[2].wins} ({game_stats[2].wins_percentage})\n'
        f'- проиграно: {game_stats[2].losses} ({game_stats[2].losses_percentage})\n'
        f'- бафф: +{snow_duel_config.user_buff(game_stats[2].amount):.2f}%\n\n'
        f'☃️ Снеговичок:\n'
        f'- текущий: {game_stats[1].current} см\n'
        f'- самый высокий: {game_stats[1].maximum} см\n'
        f'- попыток слепить: {game_stats[1].all_attempts} шт\n\n'
        f'🔮 Предсказания:\n'
        f'- написано: {prediction_stats.written}\n'
        f'- получено: {prediction_stats.received}\n\n'
    )
