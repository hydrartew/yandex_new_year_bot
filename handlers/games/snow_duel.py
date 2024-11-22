import asyncio

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from icecream import ic

from db.db_redis import SnowDuelDBQueries
from filters import GroupChat
from handlers import dp
from schemas import WhoMoves, SnowDuelRoom


def hud(_data: SnowDuelRoom):
    return (
        '<blockquote>❄️🔫 Снежная дуэль</blockquote>\n'
        f'Расстояние: {_data.distance} шагов\n\n'
        f'Раунд: {_data.current_round}\n\n'
        f'@{_data.owner.tg_username}: {'❤️❤️'.replace('❤️', '💔', _data.opponent.points)}\n'
        f'@{_data.opponent.tg_username}: {'❤️❤️'.replace('❤️', '💔', _data.owner.points)}\n\n'
    )


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
            text='Принять вызов', callback_data='start_snow_duel')]])
    )

    await SnowDuelDBQueries(
        chat_id=message.chat.id,
        message_id=send_message.message_id
    ).create_room(
        owner_tg_user_id=message.from_user.id,
        owner_tg_tg_username=message.from_user.username,
        distance=25,  # TODO: добавить рандом конфиг
        who_moves=WhoMoves.owner  # TODO: добавить рандом конфиг
    )


@dp.callback_query(F.data == 'start_snow_duel')
async def game_snow_duel_call(call: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()

    if current_state == 'SnowDuelState:is_owner':
        await call.answer(
            'Ты не можешь принять свой же вызов. Ждем оппонента...',
            show_alert=True,
            cache_time=20
        )
        return

    if current_state == 'SnowDuelState:is_opponent':
        await call.answer(
            'У тебя есть незавершенная дуэль, если хочешь отменить её, напиши /cancel_snow_duel',
            show_alert=True,
            cache_time=3
        )
        return

    await state.set_state(SnowDuelState.is_opponent)

    _data = await SnowDuelDBQueries(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    ).add_opponent_to_room(
        opponent_tg_user_id=call.from_user.id,
        opponent_tg_tg_username=call.from_user.username
    )

    if not _data.room_exists:
        await call.answer('Дуэль уже закончилась или не существует', show_alert=True, cache_time=120)
        return

    if _data.room_already_has_opponent:
        await call.answer('Ты не участвуешь в этой дэули', show_alert=True, cache_time=120)
        return

    if _data.user_is_owner_already_in_room:
        await call.answer('Ты уже участвуешь в этой дуэли', show_alert=True, cache_time=20)
        return

    if _data.snow_duel_data.who_moves == WhoMoves.owner:
        who_throw = _data.snow_duel_data.owner.tg_username
        who_get = _data.snow_duel_data.opponent.tg_username
    else:
        who_throw = _data.snow_duel_data.opponent.tg_username
        who_get = _data.snow_duel_data.owner.tg_username

    await call.message.edit_text(
        text=hud(_data.snow_duel_data) + f'🔛 @{who_throw} - бросает',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
            text=f'Бросить ❄️ в @{who_get}', callback_data='throw_snowball')]])
    )


@dp.callback_query(SnowDuelState.is_opponent)
@dp.callback_query(F.data == 'throw_snowball', SnowDuelState.is_owner)
async def game_snow_duel_throw(call: CallbackQuery):
    is_hit = True  # TODO: добавить рандом конфиг

    _data = await SnowDuelDBQueries(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    ).make_move(
        tg_user_id=call.from_user.id,
        is_hit=is_hit
    )

    if not _data.user_in_room:
        await call.answer('Ты не участвуешь в этой дэули', show_alert=True, cache_time=120)
        return

    if not _data.is_current_user_move:
        await call.answer('Сейчас не твой бросок', show_alert=True, cache_time=10)
        return

    if not _data.room_exists:
        await call.answer('Дуэль уже состоялась или не существует', show_alert=True, cache_time=120)
        return

    footer = f'🔛 @{call.from_user.username} - мимо 💨'
    if is_hit:
        footer = f'🔛 @{call.from_user.username} - попал(а) 🎯'

    await call.message.edit_text(hud(_data.snow_duel_data) + footer)
    await asyncio.sleep(3)

    if _data.snow_duel_data.who_moves == WhoMoves.owner:
        who_throw = _data.snow_duel_data.owner.tg_username
        who_get = _data.snow_duel_data.opponent.tg_username
    else:
        who_throw = _data.snow_duel_data.opponent.tg_username
        who_get = _data.snow_duel_data.owner.tg_username

    await call.message.edit_text(
        text=hud(_data.snow_duel_data) + f'🔛 @{who_throw} - бросает',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
            text=f'Бросить ❄️ в @{who_get}', callback_data='throw_snowball')]])
    )


@dp.message(Command("cancel_snow_duel"))
@dp.message(F.text.casefold() == "cancel_snow_duel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        await message.reply('У тебя нет активных дуэлей')
        return

    await state.clear()
    await message.answer("Cancelling state {}".format(current_state))
