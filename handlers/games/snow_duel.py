import asyncio
import logging

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from db.db_redis import SnowDuelDBQueries
from filters import GroupChat
from handlers import dp
from keyboards.inline import ikb_throw
from loader import bot
from schemas import WhoMoves, SnowDuelRoom, TgUsernamesWhoThrowsAndWhoGets

logger = logging.getLogger('handlers')


def hud(_data: SnowDuelRoom,
        finish_game: bool = False,
        cancel_game: bool = False,
        who_canceled_game: str | None = None) -> str:

    if finish_game:

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

    if cancel_game:
        if _data.opponent is None:
            return (
                f'@{_data.owner.tg_username} предлагает сразиться в снежной дуэли ❄️🔫\n\n'
                f'Дуэль отменена'
            )
        return (
            '<blockquote>❄️🔫 Снежная дуэль (отменена)</blockquote>\n'
            f'Расстояние: {_data.distance} шагов\n\n'
            f'Раундов: {_data.current_round}\n\n'
            f'@{_data.owner.tg_username}: {'❤️❤️'.replace('❤️', '💔', _data.opponent.points)}\n'
            f'@{_data.opponent.tg_username}: {'❤️❤️'.replace('❤️', '💔', _data.owner.points)}\n\n'
            f'❌ @{who_canceled_game} - отменяет'
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
    in_game = State()


@dp.message(Command('snow_duel'), GroupChat())
async def start_game(message: Message, state: FSMContext) -> None:
    if await state.get_state() is not None:
        await message.reply('Ты уже участвуешь в дуэли, если хочешь отменить её, пропиши команду /cancel_snow_duel')
        return

    send_message = await message.answer(
        text=f'@{message.from_user.username} предлагает сразиться в снежной дуэли ❄️🔫',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
            text='Принять вызов', callback_data='start_snow_duel')]])
    )

    await state.set_state(SnowDuelState.in_game)
    await state.update_data(game_room_message_id=send_message.message_id)

    await SnowDuelDBQueries(
        chat_id=message.chat.id,
        message_id=send_message.message_id
    ).create_room(
        owner_tg_user_id=message.from_user.id,
        owner_tg_tg_username=message.from_user.username
    )


@dp.callback_query(F.data == 'start_snow_duel')
async def join_the_game(call: CallbackQuery, state: FSMContext):
    if await state.get_state() is not None:
        await call.answer(
            'Ты уже участвуешь в дуэли, если хочешь отменить её, напиши /cancel_snow_duel',
            show_alert=True,
            cache_time=3
        )
        return

    await state.set_state(SnowDuelState.in_game)
    await state.update_data(game_room_message_id=call.message.message_id)

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


@dp.callback_query(F.data == 'throw_snowball', SnowDuelState.in_game)
async def throw_snowball(call: CallbackQuery, state: FSMContext):

    _data = await SnowDuelDBQueries(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    ).make_move(
        tg_user_id=call.from_user.id
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
    if _data.is_hit:
        footer = f'🔛 @{call.from_user.username} - попал(а) 🎯'

    await call.message.edit_text(hud(_data.snow_duel_data) + footer)
    await asyncio.sleep(3)

    if _data.snow_duel_data.game_status == 'finished':
        await call.message.edit_text(hud(_data.snow_duel_data, finish_game=True))

        if call.from_user.id == _data.snow_duel_data.owner.tg_user_id:
            another_user_id = _data.snow_duel_data.opponent.tg_user_id
        else:
            another_user_id = _data.snow_duel_data.owner.tg_user_id

        await state.clear()  # для call.from_user.id

        state.key = StorageKey(
            bot_id=state.key.bot_id,
            chat_id=state.key.chat_id,
            user_id=another_user_id,
            thread_id=state.key.thread_id
        )
        await state.clear()  # для соперника

        return

    who = tg_usernames_who_throws_and_who_gets(_data.snow_duel_data)

    await call.message.edit_text(
        text=hud(_data.snow_duel_data) + f'🔛 @{who.throw} - бросает',
        reply_markup=ikb_throw
    )


@dp.message(Command("cancel_snow_duel"))
@dp.message(F.text.casefold() == "cancel_snow_duel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    if await state.get_state() is None:
        return

    state_data = await state.get_data()
    game_room_message_id = state_data.get('game_room_message_id')

    _data = await SnowDuelDBQueries(
        chat_id=message.chat.id,
        message_id=game_room_message_id
    ).cancel_game(
        initiator_tg_user_id=message.from_user.id
    )

    if _data is None:
        await state.clear()
        await message.reply("Дуэль отменена")
        return

    await state.clear()  # для initiator_tg_user_id, т.е. для message.from_user.id

    state.key = StorageKey(
        bot_id=state.key.bot_id,
        chat_id=state.key.chat_id,
        user_id=_data.another_user_id,
        thread_id=state.key.thread_id
    )
    await state.clear()  # для соперника

    await bot.edit_message_text(
        hud(
            _data.snow_duel_data,
            cancel_game=True,
            who_canceled_game=message.from_user.username
        ),
        chat_id=message.chat.id,
        message_id=game_room_message_id
    )
    await message.answer("Дуэль отменена", reply_to_message_id=game_room_message_id)


@dp.message(Command('snow', 'snow_duel', 'snowman', 'quiz'), GroupChat(), SnowDuelState.in_game)
async def check_state(message: Message) -> None:
    await message.reply(
        'Нельзя выполнить это действие, пока ты участвуешь в дуэли. '
        'Если хочешь её отменить, вызови команду /cancel_snow_duel'
    )
