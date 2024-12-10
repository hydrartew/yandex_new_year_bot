from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from configs import settings
from localization import Localization


def ikb_subscription(localization: Localization):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=localization.get('subscribe'),
                    url=settings.TELEGRAM_CHANNEL_BOT_NEWS_INVITE_LINK
                )
            ]
        ]
    )
