from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ikb_throw = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f'Бросить снежок ❄️',
                    callback_data='throw_snowball'
                )
            ]
        ]
    )
