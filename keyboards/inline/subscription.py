from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from configs import settings

ikb_subscription = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Подписаться ✅',
                    url=settings.TELEGRAM_CHANNEL_BOT_NEWS_INVITE_LINK
                )
            ]
        ]
    )
