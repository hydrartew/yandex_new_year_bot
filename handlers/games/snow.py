import logging

from aiogram.exceptions import TelegramRetryAfter
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_i18n import I18nContext
from icecream import ic

from configs import settings
from db import db_redis
from filters import GroupChat, IsSubscribed

from handlers import dp
from localization import Localization

logger = logging.getLogger('handlers')


@dp.message(Command('snow'), GroupChat(), IsSubscribed(), flags={"throttling_key": "snow"})
async def game_snow(message: Message, i18n: I18nContext) -> None:
    localization = Localization(message, i18n)

    # если сообщение без reply
    if message.reply_to_message is None:
        await send_message(
            message=message,
            text=localization.get('snowball-in-air', tg_username=message.from_user.username)
        )
        return

    # если reply на свое сообщение
    if message.from_user.username == message.reply_to_message.from_user.username:
        await send_message(
            message=message,
            text=localization.get('snowball-at-myself', tg_username=message.from_user.username)
        )
        return

    # если reply на сообщение бота
    if (message.reply_to_message.from_user.is_bot or
            message.reply_to_message.from_user.id == settings.TELEGRAM_BOT_CREATOR_ID):
        await send_message(
            message=message,
            text=localization.get(
                'snowball-in-bot',
                tg_username=message.from_user.username,
                bot_tg_username=message.reply_to_message.from_user.username
            )
        )
        return

    logger.info('/snow tg_user_id:{} reply to tg_user_id:{} in chat_id:{}, message_id:{}, reply_to_message:{}'.format(
        message.from_user.id,
        message.reply_to_message.from_user.id,
        message.chat.id,
        message.message_id,
        message.reply_to_message.message_id
    ))

    if settings.ConfigSnowSecretBox.is_secret_box():
        number_snowballs = settings.ConfigSnowSecretBox.number_snowballs()

        logger.info('/snow tg_user_id:{} gets secret_box with number_snowballs: {}'.format(
            message.from_user.id, number_snowballs
        ))

        text = localization.get(
            'snowball-is-secret-box',
            tg_username=message.from_user.username,
            number_snowballs=number_snowballs
        )

        message_was_sent = await send_message(message, text)
        if message_was_sent:
            await db_redis.snow_increase(message.from_user.id, from_tg_user_id_amount=number_snowballs)

    else:
        text = localization.get(
            'snowball-throw',
            tg_username=message.from_user.username,
            to_tg_username=message.reply_to_message.from_user.username
        )
        message_was_sent = await send_message(message, text)
        if message_was_sent:
            await db_redis.snow_increase(message.from_user.id, to_tg_user_id=message.reply_to_message.from_user.id)


async def send_message(message: Message, text: str) -> bool:
    try:
        await message.answer(text)
    except TelegramRetryAfter as err:
        logger.warning(err.message)
    else:
        return True
    return False
