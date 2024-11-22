import asyncio

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from db.db_redis import SnowDuelDBQueries
from filters import GroupChat
from handlers import dp
from keyboards.inline import ikb_throw
from schemas import WhoMoves, SnowDuelRoom, TgUsernamesWhoThrowsAndWhoGets


def hud(_data: SnowDuelRoom, end_game: bool = False):

    if end_game:

        winner = f'{_data.owner.tg_username}'
        if _data.opponent.points >= 2:
            winner = f'{_data.opponent.tg_username}'

        return (
            '<blockquote>❄️🔫 Снежная дуэль (завершена)</blockquote>\n'
            f'Расстояние: {_data.distance} шагов\n\n'
            f'Раундов: {_data.current_round}\n\n'
            f'@{_data.owner.tg_username}: {'❤️❤️'.replace('❤️', '💔', _data.opponent.points)}\n'
            f'@{_data.opponent.tg_username}: {'❤️❤️'.replace('❤️', '💔', _data.owner.points)}\n\n'
            f'🏆 @{winner} - побеждает'
        )

    return (
        '<blockquote>❄️🔫 Снежная дуэль</blockquote>\n'
        f'Расстояние: {_data.distance} шагов\n\n'
        f'Раунд: {_data.current_round}\n\n'
        f'@{_data.owner.tg_username}: {'❤️❤️'.replace('❤️', '💔', _data.opponent.points)}\n'
        f'@{_data.opponent.tg_username}: {'❤️❤️'.replace('❤️', '💔', _data.owner.points)}\n\n'
    )


def tg_usernames_who_throws_and_who_gets(_data: SnowDuelRoom) -> TgUsernamesWhoThrowsAndWhoGets:
    if _data.who_moves == WhoMoves.owner:
        return TgUsernamesWhoThrowsAndWhoGets(
            throw=_data.owner.tg_username,
            get=_data.opponent.tg_username
        )
    return TgUsernamesWhoThrowsAndWhoGets(
        throw=_data.opponent.tg_username,
        get=_data.owner.tg_username
    )


class SnowDuelState(StatesGroup):
    is_owner = State()
    is_opponent = State()


@dp.message(Command('snow_duel'), GroupChat())
async def game_snow_duel(message: Message, state: FSMContext) -> None:

    if await state.get_state() is not None:
        await message.reply('Ты уже участвуешь в дуэли, если хочешь отменить её, пропиши команду /cancel_snow_duel')
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

    if await state.get_state() is not None:
        await call.answer(
            'Ты уже участвуешь в дуэли, если хочешь отменить её, напиши /cancel_snow_duel',
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

    who = tg_usernames_who_throws_and_who_gets(_data.snow_duel_data)

    await call.message.edit_text(
        text=hud(_data.snow_duel_data) + f'🔛 @{who.throw} - бросает',
        reply_markup=ikb_throw
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
        await call.answer('Сейчас не твой бросок', show_alert=True, cache_time=3)
        return

    if not _data.room_exists:
        await call.answer('Дуэль уже состоялась или не существует', show_alert=True, cache_time=120)
        return

    footer = f'🔛 @{call.from_user.username} - мимо 💨'
    if is_hit:
        footer = f'🔛 @{call.from_user.username} - попал(а) 🎯'

    await call.message.edit_text(hud(_data.snow_duel_data) + footer)
    await asyncio.sleep(3)

    if _data.snow_duel_data.game_status == 'finished':
        await call.message.edit_text(hud(_data.snow_duel_data, end_game=True))
        return

    who = tg_usernames_who_throws_and_who_gets(_data.snow_duel_data)

    await call.message.edit_text(
        text=hud(_data.snow_duel_data) + f'🔛 @{who.throw} - бросает',
        reply_markup=ikb_throw
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
