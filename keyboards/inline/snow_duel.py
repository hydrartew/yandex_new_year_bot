from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from localization import Localization


def ikb_throw(localization: Localization):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=localization.get('throw-snowball'),
                    callback_data='throw_snowball'
                )
            ]
        ]
    )


def ikb_start_snow_duel(localization: Localization):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=localization.get('take-challenge'),
                    callback_data='start_snow_duel'
                )
            ]
        ]
    )
