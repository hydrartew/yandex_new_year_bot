from aiogram.filters import Command
from aiogram.types import Message
from aiogram_i18n import I18nContext

from configs import settings
from db import db_redis, db_ydb
from filters import IsSubscribed

from loader import dp
from localization import Localization


@dp.message(Command('stats', 'profile'), IsSubscribed(), flags={"throttling_key": "stats"})
async def my_stats(message: Message, i18n: I18nContext) -> None:
    localization = Localization(message, i18n)

    game_stats = await db_redis.get_stats(message.from_user.id)
    prediction_stats = await db_ydb.get_prediction_stats(message.from_user.id)

    await message.reply(
        localization.get(
            'stats',
            tg_username=message.from_user.username,
            throw=game_stats[0].throw,
            get=game_stats[0].get,
            wins=game_stats[2].wins,
            wins_percentage=game_stats[2].wins_percentage,
            losses=game_stats[2].losses,
            losses_percentage=game_stats[2].losses_percentage,
            buff=f'{settings.ConfigSnowDuel.user_buff(game_stats[2].amount):.0%}',
            current=game_stats[1].current,
            maximum=game_stats[1].maximum,
            all_attempts=game_stats[1].all_attempts,
            received=prediction_stats.received
        )
    )
