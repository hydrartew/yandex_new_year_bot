import asyncio
import logging

from aiogram.exceptions import TelegramRetryAfter
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_i18n import I18nContext
from tenacity import retry, stop_after_attempt, before_sleep_log, wait_fixed

from configs import settings
from db.db_redis import update_snowman
from filters import GroupChat, IsSubscribed
from handlers import dp
from localization import Localization

logger = logging.getLogger(__name__)


@dp.message(Command('snowman'), GroupChat(), IsSubscribed(), flags={"throttling_key": "snowman"})
async def game_snowman(message: Message, i18n: I18nContext) -> None:
    localization = Localization(message, i18n)

    list_text = message.text.split()
    if len(list_text) != 2 or not list_text[1].isdigit() or int(list_text[1]) > 10 or int(list_text[1]) < 1:
        await send_message(message, localization.get('snowman-bad-request'))
        return

    height_increased = int(list_text[1])
    snowman_data = await update_snowman(message.from_user.id, height_increased)

    snowman_fall = settings.ConfigSnowmanFallingChances(height_increased)

    # если снеговик упал и НЕ первый ход
    if snowman_fall.is_fall and (snowman_data.current - height_increased != 0):
        text = localization.get(
            'snowman-fall',
            tg_username=message.from_user.username,
            height_increased=height_increased,
            ths_percentage_falling_chance=f'{snowman_fall.ths_percentage_falling_chance:.0%}'
        )
        await update_snowman(message.from_user.id, -1)
    else:
        text = localization.get(
            'snowman-increased',
            tg_username=message.from_user.username,
            height_increased=height_increased,
            current_height=snowman_data.current
        )

    await send_message_with_retries(message, text)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_fixed(0.5),
    before_sleep=before_sleep_log(logger, logging.INFO)
)
async def send_message_with_retries(message: Message, text: str) -> None:
    try:
        await message.answer(text)
    except TelegramRetryAfter as err:
        logger.warning(err.message)
        await asyncio.sleep(err.retry_after)
        raise


async def send_message(message: Message, text: str) -> None:
    try:
        await message.answer(text)
    except TelegramRetryAfter as err:
        logger.warning(err.message)
    finally:
        return
