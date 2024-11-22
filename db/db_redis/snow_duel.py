import logging
from datetime import datetime

import redis

from db.db_redis.connection import create_redis_client, redis_retry
from schemas import SnowDuelRoom, SnowDuelUser, WhoMoves, MakeMove, AddOpponentToRoom

logger = logging.getLogger('db.redis')


class SnowDuelDBQueries:
    def __init__(self, chat_id: int, message_id: int):
        self.pattern = 'snow_duel:{}:{}:data'
        self.limit_points_to_win = 2

        self.hash_name = self.pattern.format(chat_id, message_id)

    @redis_retry()
    async def create_room(self, owner_tg_user_id: int, distance: int, who_moves: WhoMoves) -> None:
        logger.info(f'Creating a room {self.hash_name} with owner tg_user_id:{owner_tg_user_id} for snow_duel')

        value = SnowDuelRoom(
            game_status='created',
            owner=SnowDuelUser(
                tg_user_id=owner_tg_user_id
            ),
            who_moves=who_moves,
            distance=distance,
            dttm_created=datetime.now()
        )

        r = await create_redis_client()
        try:
            await r.set(self.hash_name, value.model_dump_json())
        except redis.ConnectionError as e:
            logger.error(f'Error connecting to Redis: {e}')
            raise
        except redis.TimeoutError as e:
            logger.error(f'Timeout when trying to connect to Redis: {e}')
            raise
        except Exception as e:
            logger.critical(f"An unexpected error: {e}")
            raise
        finally:
            await r.aclose()

    @redis_retry()
    async def add_opponent_to_room(self, opponent_tg_user_id: int) -> AddOpponentToRoom:
        logger.info(f'Add opponent tg_user_id:{opponent_tg_user_id} to the room {self.hash_name} for snow_duel')

        r = await create_redis_client()
        try:
            room_data = await r.get(self.hash_name)

            if room_data is None:
                logger.error(f'Room {self.hash_name} not found for snow_duel')
                return AddOpponentToRoom(room_exists=False)

            room_data = SnowDuelRoom.model_validate_json(room_data)

            if room_data.game_status != 'created':
                logger.warning(f'Can not add opponent because '
                               f'the room {self.hash_name} is in status "{room_data.game_status}"')
                return AddOpponentToRoom(room_exists=False)

            if opponent_tg_user_id == room_data.owner.tg_user_id:
                logger.info(f'Opponent tg_user_id:{opponent_tg_user_id} is the owner of the room')
                return AddOpponentToRoom(user_is_owner_already_in_room=True)

            if room_data.opponent is not None:
                logger.warning(f'Room {self.hash_name} already has '
                               f'an opponent tg_user_id:{room_data.opponent.tg_user_id}')
                return AddOpponentToRoom(room_already_has_opponent=True)

            room_data.game_status = 'in_progress'
            room_data.opponent = SnowDuelUser(tg_user_id=opponent_tg_user_id)

            await r.set(self.hash_name, room_data.model_dump_json())

            return AddOpponentToRoom()

        except redis.ConnectionError as e:
            logger.error(f'Error connecting to Redis: {e}')
            raise
        except redis.TimeoutError as e:
            logger.error(f'Timeout when trying to connect to Redis: {e}')
            raise
        except Exception as e:
            logger.critical(f"An unexpected error: {e}")
            raise
        finally:
            await r.aclose()

    @redis_retry()
    async def make_move(self, tg_user_id: int, is_hit: bool) -> MakeMove:
        logger.info(f'tg_user_id:{tg_user_id} make a move in {self.hash_name}')

        r = await create_redis_client()
        try:
            room_data = await r.get(self.hash_name)

            if room_data is None:
                logger.error(f'Room {self.hash_name} not found for snow_duel')
                return MakeMove(room_exists=False)

            room_data = SnowDuelRoom.model_validate_json(room_data)

            if room_data.game_status != 'in_progress':
                logger.warning(f'Can not make a move because '
                               f'the room {self.hash_name} is in status "{room_data.game_status}"')
                return MakeMove(room_exists=False)

            if tg_user_id == room_data.owner.tg_user_id:
                if room_data.who_moves == WhoMoves.owner:
                    current_player, who_move_next = room_data.owner, WhoMoves.opponent
                else:
                    return MakeMove(is_current_user_move=False)
            elif tg_user_id == room_data.opponent.tg_user_id:
                if room_data.who_moves == WhoMoves.opponent:
                    current_player, who_move_next = room_data.opponent, WhoMoves.owner
                else:
                    return MakeMove(is_current_user_move=False)
            else:
                return MakeMove(user_in_room=False)

            current_player.moves += 1
            current_player.dttm_last_move = datetime.now()

            if is_hit:
                current_player.points += 1

            if current_player.points >= self.limit_points_to_win:
                room_data.game_status = 'finished'

            room_data.who_moves = who_move_next

            await r.set(self.hash_name, room_data.model_dump_json())

            return MakeMove(snow_duel_data=room_data)

        except redis.ConnectionError as e:
            logger.error(f'Error connecting to Redis: {e}')
            raise
        except redis.TimeoutError as e:
            logger.error(f'Timeout when trying to connect to Redis: {e}')
            raise
        except Exception as e:
            logger.critical(f"An unexpected error: {e}")
            raise
        finally:
            await r.aclose()
