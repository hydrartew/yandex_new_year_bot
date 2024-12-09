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

ikb_start_snow_duel = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Принять вызов',
                callback_data='start_snow_duel'
            )
        ]
    ]
)
