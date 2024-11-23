import asyncio
import logging
import random
import re

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
from schemas import WhoMoves, SnowDuelRoom, TgUsernamesWhoThrowsAndWhoGets


logger = logging.getLogger('handlers')


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
    in_game = State()


@dp.message(Command('snow_duel'), GroupChat())
async def game_snow_duel(message: Message, state: FSMContext) -> None:
    if await state.get_state() is not None:
        await message.reply('Ты уже участвуешь в дуэли, если хочешь отменить её, пропиши команду /cancel_snow_duel')
        return

    await state.set_state(SnowDuelState.in_game)

    send_message = await message.answer(
        text=f'@{message.from_user.username} предлагает сразиться в снежной дуэли ❄️🔫',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
            text='Принять вызов', callback_data='start_snow_duel')]])
    )

    snow_duel_config = SnowDuelConfig()

    await SnowDuelDBQueries(
        chat_id=message.chat.id,
        message_id=send_message.message_id
    ).create_room(
        owner_tg_user_id=message.from_user.id,
        owner_tg_tg_username=message.from_user.username,
        distance=snow_duel_config.distance,
        who_moves=snow_duel_config.who_moves_first
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

    await state.set_state(SnowDuelState.in_game)

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
async def game_snow_duel_throw(call: CallbackQuery, state: FSMContext):
    steps_extracted = re.findall(r'\d+', call.message.text.split('\n')[1])[0]  # костыль

    if not steps_extracted.isdigit():
        logger.error(f'Failed to extract steps in {call.message.text}')
        steps_extracted = 30

    is_hit = SnowDuelConfig().is_hit(int(steps_extracted))

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


# TODO: добавить state SnowDuelState.in_game и протестить
@dp.message(Command("cancel_snow_duel"))
@dp.message(F.text.casefold() == "cancel_snow_duel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.reply("Дуэль отменена".format(current_state))


class SnowDuelConfig:
    def __init__(self):
        """Chance configuration for snow_duel"""
        self.config = {  # TODO: вынести в отдельный json-файл
            "distance": {
                "bottom_bound": {
                    "steps": 25,  # inclusive
                    "hit_chance": "60%"
                },
                "upper_bound": {
                    "steps": 45,  # inclusive
                    "hit_chance": "40%"
                }
            },
            "chance_first_move": {
                "owner": "50%",
                "opponent": "50%"
            }
        }

    @property
    def distance(self) -> int:
        _config = self.config['distance']
        return random.randint(_config['bottom_bound']['steps'], _config['upper_bound']['steps'])

    def hit_chance(self, steps: int) -> float:
        _config = self.config['distance']

        upper_steps = _config['upper_bound']['steps']
        bottom_steps = _config['bottom_bound']['steps']

        if not (bottom_steps <= steps <= upper_steps):
            raise ValueError(f"Steps must be between distance.bottom_bound.steps:{bottom_steps} "
                             f"and distance.upper_bound.steps:{upper_steps}")

        bottom_hit_chance = int(_config['bottom_bound']['hit_chance'].strip('%'))
        upper_hit_chance = int(_config['upper_bound']['hit_chance'].strip('%'))

        chance_1_step = (bottom_hit_chance - upper_hit_chance) / (upper_steps - bottom_steps)

        current_step_hit_chance = bottom_hit_chance - ((steps - bottom_steps) * chance_1_step)

        return round(current_step_hit_chance, 2)

    def is_hit(self, steps: int) -> bool:
        _hit_chance = self.hit_chance(steps)
        return random.choices([
            True,
            False
        ], weights=[
            _hit_chance,
            100-_hit_chance
        ])[0]

    @property
    def who_moves_first(self) -> WhoMoves:
        _config = self.config['chance_first_move']

        return random.choices([
            WhoMoves.owner,
            WhoMoves.opponent
        ], weights=[
            int(_config['owner'].strip('%')),
            int(_config['opponent'].strip('%'))
        ])[0]
