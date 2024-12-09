import logging
from typing import Literal

from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram_i18n import I18nContext

from configs import settings
from filters import GroupChat, PrivateChat, IsSubscribed
from keyboards.inline import ikb_welcome_private_chat, ikb_welcome_group_chat
from loader import dp
from localization import Localization

logger = logging.getLogger('handlers')

flags = {"throttling_key": "help"}


async def send_help_message(message: Message, i18n: I18nContext, reply_markup: InlineKeyboardMarkup,
                            private_chat_footer: Literal['true', 'false'] = 'false') -> None:
    try:
        await message.answer(
            text=Localization(message, i18n).get(
                'help-text',
                message_text=message.text.removeprefix('/'),
                TELEGRAM_CHANNEL_BOT_NEWS_INVITE_LINK=settings.TELEGRAM_CHANNEL_BOT_NEWS_INVITE_LINK,
                TELEGRAM_CHANNEL_BOT_NEWS_NAME=settings.TELEGRAM_CHANNEL_BOT_NEWS_NAME,
                YANDEX_FORM_FEEDBACK_LINK=settings.YANDEX_FORM_FEEDBACK_LINK,
                YANDEX_FORM_FEEDBACK_LINK_WITH_PRE_COMPLETION=settings.YANDEX_FORM_FEEDBACK_LINK_WITH_PRE_COMPLETION,
                private_chat_footer=private_chat_footer
            ),
            reply_markup=reply_markup
        )
    except TelegramForbiddenError:
        logger.warning(
            'The message could not be sent because bot was blocked by the tg_user_id: {}'.format(message.from_user.id)
        )


@dp.message(Command('help', 'start'), PrivateChat(), IsSubscribed(), flags=flags)
async def welcome_private_chat(message: Message, i18n: I18nContext) -> None:
    await send_help_message(message, i18n, ikb_welcome_private_chat, 'true')


@dp.message(Command('help', 'start'), GroupChat(), IsSubscribed(), flags=flags)
async def welcome_group_chat(message: Message, i18n: I18nContext) -> None:
    await send_help_message(message, i18n, ikb_welcome_group_chat)
