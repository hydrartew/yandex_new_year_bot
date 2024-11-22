from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def ikb_throw(who_get: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f'Бросить ❄️ в @{who_get}',
                    callback_data='throw_snowball'
                )
            ]
        ]
    )
