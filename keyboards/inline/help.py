from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from configs import settings

ikb_welcome_private_chat = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=settings.TELEGRAM_CHANNEL_BOT_NEWS_NAME,
                    url=settings.TELEGRAM_CHANNEL_BOT_NEWS_INVITE_LINK
                ),
                InlineKeyboardButton(
                    text='Форма',
                    url=settings.YANDEX_FORM_FEEDBACK_LINK
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'Добавить бота в группу',
                    url='https://t.me/{}?startgroup=sgl'.format(settings.TELEGRAM_BOT_LOGIN)
                )
            ]
        ]
    )


ikb_welcome_group_chat = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=settings.TELEGRAM_CHANNEL_BOT_NEWS_NAME,
                    url=settings.TELEGRAM_CHANNEL_BOT_NEWS_INVITE_LINK
                ),
                InlineKeyboardButton(
                    text='Форма',
                    url=settings.YANDEX_FORM_FEEDBACK_LINK
                )
            ]
        ]
    )
