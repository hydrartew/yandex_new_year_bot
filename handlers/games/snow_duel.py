import datetime

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from icecream import ic

from filters import GroupChat
from handlers import dp


class SnowDuelState(StatesGroup):
    is_owner = State()
    is_opponent = State()


@dp.message(Command('snow_duel'), GroupChat())
async def game_snow_duel(message: Message, state: FSMContext) -> None:
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

    await state.set_state(SnowDuelState.is_owner)

    send_message = await message.answer(
        text=f'@{message.from_user.username} предлагает сразиться в снежной дуэли ❄️🔫',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
            text='Принять вызов', callback_data=f'start_snow_duel {message.from_user.id}')]])
    )


@dp.callback_query(F.data.split()[0] == 'start_snow_duel')
async def game_snow_duel_call(call: CallbackQuery, state: FSMContext):
    owner_id = int(call.data.split()[1])

    if await state.get_state() is not None:
        await call.answer('Ты уже участвуешь в дуэли ❄️🔫', show_alert=True, cache_time=120)
        return

    await state.set_state(SnowDuelState.is_opponent)

    # if call.message.message_id != opponent_data.get('message_id'):
    #     await call.answer('Ты не можешь принять участие в этой дуэли', show_alert=True, cache_time=120)
    #     return

    await call.message.edit_text(
        text=f'Снежная дуэль ❄️🔫\n@player1 VS @{call.from_user.username}',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
            text='Бросить снежок в оппонента', callback_data='throw_snowball')]])
    )


@dp.message(Command("cancel_snow_duel"))
@dp.message(F.text.casefold() == "cancel_snow_duel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Cancelling state {}".format(current_state))


# @dp.message(SnowDuelState.waiting_for_opponent)
# async def process_unknown_write_bots(message: Message, state: FSMContext) -> None:
#     data = await state.get_data()
#     ic(data)
#     await message.reply("I don't understand you :(")
