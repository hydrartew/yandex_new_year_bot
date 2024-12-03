from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ikb_welcome_private_chat = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f'Форма',
                    url='https://forms.yandex-team.ru/ext/surveys/13711111/'
                ),
                InlineKeyboardButton(
                    text=f'YNYB News',
                    url='https://nda.ya.ru/t/8Ve9IRKc79adW7'
                )
            ],
            [
                InlineKeyboardButton(
                    text=f'Добавить бота в группу',
                    url='https://t.me/yandex_new_year_bot?startgroup=sgl'
                )
            ]
        ]
    )


ikb_welcome_group_chat = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f'Форма',
                    url='https://forms.yandex-team.ru/ext/surveys/13711111/'
                ),
                InlineKeyboardButton(
                    text=f'YNYB News',
                    url='https://nda.ya.ru/t/8Ve9IRKc79adW7'
                )
            ]
        ]
    )
