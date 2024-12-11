import asyncio
import logging

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message, CallbackQuery
from aiogram_i18n import I18nContext

from db.db_redis import SnowDuelDBQueries
from filters import GroupChat, IsSubscribed
from handlers import dp
from keyboards.inline import ikb_throw, ikb_start_snow_duel
from loader import bot
from localization import Localization
from schemas import WhoMoves, SnowDuelRoom, TgUsernamesWhoThrowsAndWhoGets

logger = logging.getLogger('handlers')


class SnowDuelState(StatesGroup):
    in_game = State()


@dp.message(Command('snow_duel'), GroupChat(), IsSubscribed(), flags={"throttling_key": "snow_duel_start"})
async def start_game(message: Message, state: FSMContext, i18n: I18nContext) -> None:
    localization = Localization(message, i18n)

    if await state.get_state() is not None:
        await message.reply(localization.get('snow-duel-already-in-duel'))
        return

    send_message = await message.answer(
        text=localization.get('snow-duel-start', tg_username=message.from_user.username),
        reply_markup=ikb_start_snow_duel(localization)
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


@dp.callback_query(F.data == 'start_snow_duel', IsSubscribed())
async def join_the_game(call: CallbackQuery, state: FSMContext, i18n: I18nContext) -> None:
    localization = Localization(call, i18n)

    if await state.get_state() is not None:
        await call.answer(
            text=localization.get('snow-duel-already-in-duel'),
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
        await call.answer(localization.get('snow-duel-not-room-exists'), show_alert=True, cache_time=120)
        return

    if _data.room_already_has_opponent:
        await call.answer(localization.get('snow-duel-room-already-has-opponent'), show_alert=True, cache_time=120)
        return

    if _data.user_is_owner_already_in_room:
        await call.answer(localization.get('snow-duel-user-is-owner-already-in-room'), show_alert=True, cache_time=20)
        return

    who = tg_usernames_who_throws_and_who_gets(_data.snow_duel_data)

    await call.message.edit_text(
        text=hud(_data.snow_duel_data, localization) + localization.get('snow-duel-throws', tg_username=who.throw),
        reply_markup=ikb_throw(localization)
    )


@dp.callback_query(F.data == 'throw_snowball', SnowDuelState.in_game, IsSubscribed())
async def throw_snowball(call: CallbackQuery, state: FSMContext, i18n: I18nContext) -> None:
    localization = Localization(call, i18n)

    _data = await SnowDuelDBQueries(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    ).make_move(
        tg_user_id=call.from_user.id
    )

    if not _data.user_in_room:
        await call.answer(localization.get('snow-duel-room-already-has-opponent'), show_alert=True, cache_time=120)
        return

    if not _data.is_current_user_move:
        await call.answer(localization.get('snow-duel-is-current-user-move'), show_alert=True, cache_time=3)
        return

    if not _data.room_exists:
        await call.answer(localization.get('snow-duel-not-room-exists'), show_alert=True, cache_time=120)
        return

    footer = localization.get('snow-duel-away', tg_username=call.from_user.username)
    if _data.is_hit:
        footer = localization.get('snow-duel-hit', tg_username=call.from_user.username)

    await call.message.edit_text(hud(_data.snow_duel_data, localization) + footer)
    await asyncio.sleep(3)

    if _data.snow_duel_data.game_status == 'finished':
        await call.message.edit_text(hud(_data.snow_duel_data, localization, finish_game=True))

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
        text=hud(_data.snow_duel_data, localization) + localization.get('snow-duel-throws', tg_username=who.throw),
        reply_markup=ikb_throw(localization)
    )


@dp.message(Command("cancel_snow_duel"), IsSubscribed(), flags={"throttling_key": "snow_duel_cancel"})
@dp.message(F.text.casefold() == "cancel_snow_duel", IsSubscribed(), flags={"throttling_key": "snow_duel_cancel"})
async def cancel_handler(message: Message, state: FSMContext, i18n: I18nContext) -> None:
    localization = Localization(message, i18n)

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
        await message.reply(localization.get('snow-duel-cancelled'))
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
            localization,
            cancel_game=True,
            who_canceled_game=message.from_user.username
        ),
        chat_id=message.chat.id,
        message_id=game_room_message_id
    )
    await message.answer(localization.get('snow-duel-cancelled'), reply_to_message_id=game_room_message_id)


@dp.message(
    Command('snow', 'snow_duel', 'snowman', 'quiz'),
    GroupChat(),
    SnowDuelState.in_game,
    IsSubscribed(),
    flags={"throttling_key": "snow_duel_in_game"}
)
async def check_state(message: Message, i18n: I18nContext) -> None:
    localization = Localization(message, i18n)
    await message.reply(localization.get('snow-duel-check-state'))


def health_points(_data: SnowDuelRoom) -> str:
    text = f'@{_data.owner.tg_username}: {"❤️❤️".replace("❤️", "💔", _data.opponent.points)}'
    if _data.opponent is not None:
        text += f'\n@{_data.opponent.tg_username}: {"❤️❤️".replace("❤️", "💔", _data.owner.points)}'

    return text


def hud(_data: SnowDuelRoom,
        localization: Localization,
        finish_game: bool = False,
        cancel_game: bool = False,
        who_canceled_game: str | None = None) -> str:
    base_info = localization.get(
        'snow-duel-base-info',
        distance=_data.distance,
        rounds=_data.current_round,
        health_points_data=health_points(_data)
    )

    if finish_game:
        winner = _data.owner.tg_username if _data.owner.points >= 2 else _data.opponent.tg_username

        return (
            f'{localization.get("snow-duel-finished")}\n'
            f'{base_info}\n\n'
            f'{localization.get("snow-duel-winner", tg_username=winner)}'
        )

    if cancel_game:
        if _data.opponent is None:
            return (
                f'{localization.get("snow-duel-start", tg_username=_data.owner.tg_username)}\n\n'
                f'{localization.get("snow-duel-cancelled")}'
            )
        return (
            f'{localization.get("snow-duel-cancelled-2")}\n'
            f'{base_info}\n\n'
            f'{localization.get("snow-duel-cancels", tg_username=who_canceled_game)}'
        )

    return (
        f'{localization.get("snow-duel-title-blockquote")}\n'
        f'{base_info}\n\n'
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
