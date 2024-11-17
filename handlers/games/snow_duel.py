from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from handlers import dp


@dp.message(Command('snow_duel'))
async def game_snow_duel(message: Message) -> None:
    # если сообщение без reply
    if message.reply_to_message is None:
        await message.reply(f'Для участия в снежной дуэли ❄️🔫 нужно выбрать оппонента, '
                            f'отправь /snow_duel в ответ на сообщение другого человека')
        return

    # если reply на сообщение бота
    if message.reply_to_message.from_user.is_bot:
        await message.reply('Бот не может участвовать в снежной дуэли ❄️🔫, выбери человекоподобного оппонента')
        return

    # если reply на свое сообщение
    if message.from_user.username == message.reply_to_message.from_user.username:
        await message.answer('Ты не можешь вызвать на снежную дуэль ❄️🔫 самого себя, выбери оппонента')
        return

    await message.answer(
        text=f'@{message.from_user.username} предлагает сразиться в снежной дуэли ❄️🔫',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
            text='Принять вызов', callback_data='join_snow_duel')]])
    )


@dp.callback_query(F.data == 'join_snow_duel')
async def game_snow_duel_call(call: CallbackQuery):
    if call.message.text.removeprefix('@').startswith(call.from_user.username):
        await call.answer('Ты уже участвуешь в дуэли!')
        return

    await call.message.edit_text(
        text=f'Снежная дуэль ❄️🔫\n@player1 VS @{call.from_user.username}',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
            text='Бросить снежок в оппонента', callback_data='throw_snowball')]])
    )
