from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from configs import settings
from localization import Localization


def ikb_welcome_private_chat(localization: Localization):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=settings.TELEGRAM_CHANNEL_BOT_NEWS_NAME,
                    url=settings.TELEGRAM_CHANNEL_BOT_NEWS_INVITE_LINK
                ),
                InlineKeyboardButton(
                    text=localization.get('form'),
                    url=settings.YANDEX_FORM_FEEDBACK_LINK
                )
            ],
            [
                InlineKeyboardButton(
                    text=localization.get('add-bot-to-group'),
                    url='https://t.me/{}?startgroup=sgl'.format(settings.TELEGRAM_BOT_LOGIN)
                )
            ]
        ]
    )


def ikb_welcome_group_chat(localization: Localization):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=settings.TELEGRAM_CHANNEL_BOT_NEWS_NAME,
                    url=settings.TELEGRAM_CHANNEL_BOT_NEWS_INVITE_LINK
                ),
                InlineKeyboardButton(
                    text=localization.get('form'),
                    url=settings.YANDEX_FORM_FEEDBACK_LINK
                )
            ]
        ]
    )
