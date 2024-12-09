import logging

from aiogram.filters import Command
from aiogram.types import Message
from aiogram_i18n import I18nContext

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
        await message.answer(
            text=localization.get('snowball-in-air', tg_username=message.from_user.username)
        )
        return

    # если reply на сообщение бота
    if message.reply_to_message.from_user.is_bot:
        await message.answer(
            text=localization.get(
                'snowball-in-bot',
                tg_username=message.from_user.username,
                bot_tg_username=message.reply_to_message.from_user.username
            )
        )
        return

    # если reply на свое сообщение
    if message.from_user.username == message.reply_to_message.from_user.username:
        await message.answer(
            text=localization.get('snowball-at-myself', tg_username=message.from_user.username)
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

        await message.answer(
            text=localization.get(
                'snowball-is-secret-box',
                tg_username=message.from_user.username,
                number_snowballs=number_snowballs
            )
        )
        await db_redis.snow_increase(message.from_user.id, from_tg_user_id_amount=number_snowballs)

    else:
        await message.answer(
            text=localization.get(
                'snowball-throw',
                tg_username=message.from_user.username,
                to_tg_username=message.reply_to_message.from_user.username
            )
        )
        await db_redis.snow_increase(message.from_user.id, to_tg_user_id=message.reply_to_message.from_user.id)
