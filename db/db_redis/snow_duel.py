import logging
from datetime import datetime

import redis

from configs import settings
from db.db_redis.connection import create_redis_client, redis_retry
from schemas import SnowDuelRoom, SnowDuelUser, WhoMoves, MakeMove, AddOpponentToRoom, SnowDuelUserStats, CancelGame

logger = logging.getLogger('db.redis')


class SnowDuelDBQueries:
    def __init__(self, chat_id: int, message_id: int):
        self.game_data_pattern = 'snow_duel:{}:{}:data'
        self.hash_name = self.game_data_pattern.format(chat_id, message_id)

        self.user_data_pattern = 'tg_user_id:{}:snow_duel'
        self.limit_points_to_win = 2

    @redis_retry()
    async def create_room(self, owner_tg_user_id: int, owner_tg_tg_username: str) -> None:

        logger.info(f'tg_user_id:{owner_tg_user_id} creating a room {self.hash_name}')

        distance = settings.ConfigSnowDuel.get_random_distance()

        value = SnowDuelRoom(
            game_status='created',
            owner=SnowDuelUser(
                tg_user_id=owner_tg_user_id,
                tg_username=owner_tg_tg_username,
                hit_chance=settings.ConfigSnowDuel.hit_chance(distance)
            ),
            who_moves=settings.ConfigSnowDuel.who_moves_first(),
            distance=distance,
            dttm_created=datetime.now()
        )

        r = await create_redis_client()
        try:
            user_stats = SnowDuelUserStats.model_validate(
                await r.hgetall(self.user_data_pattern.format(owner_tg_user_id))
            )
            value.owner.hit_chance += settings.ConfigSnowDuel.user_buff(user_stats.amount)

            await r.set(self.hash_name, value.model_dump_json())
            logger.info(f'The room {self.hash_name} was created successfully')

        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.error('Error connecting to Redis while tg_user_id:{} creating a room {}: {}'.format(
                owner_tg_user_id, self.hash_name, e
            ))
            raise
        except Exception as e:
            logger.critical('An unexpected error while tg_user_id:{} creating a room {}: {}'.format(
                owner_tg_user_id, self.hash_name, e
            ))
            raise
        finally:
            await r.aclose()

    @redis_retry()
    async def add_opponent_to_room(self, opponent_tg_user_id: int, opponent_tg_tg_username: str) -> AddOpponentToRoom:
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

            user_stats = SnowDuelUserStats.model_validate(
                await r.hgetall(self.user_data_pattern.format(opponent_tg_user_id))
            )

            hit_chance = (
                    settings.ConfigSnowDuel.hit_chance(room_data.distance) +
                    settings.ConfigSnowDuel.user_buff(user_stats.amount)
            )

            room_data.opponent = SnowDuelUser(
                tg_user_id=opponent_tg_user_id,
                tg_username=opponent_tg_tg_username,
                hit_chance=hit_chance
            )

            await r.set(self.hash_name, room_data.model_dump_json())

            logger.info(f'Opponent tg_user_id:{opponent_tg_user_id} added to the room {self.hash_name} successfully')
            return AddOpponentToRoom(snow_duel_data=room_data)

        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.error('Error connecting to Redis while tg_user_id:{} adding to room {}: {}'.format(
                opponent_tg_user_id, self.hash_name, e
            ))
            raise
        except Exception as e:
            logger.critical('An unexpected error while tg_user_id:{} adding to room {}: {}'.format(
                opponent_tg_user_id, self.hash_name, e
            ))
            raise
        finally:
            await r.aclose()

    @redis_retry()
    async def make_move(self, tg_user_id: int) -> MakeMove:
        logger.info(f'tg_user_id:{tg_user_id} make a move in {self.hash_name}')

        r = await create_redis_client()
        try:
            room_data = await r.get(self.hash_name)

            if room_data is None:
                logger.error(f'Room {self.hash_name} not found for snow_duel for tg_user_id:{tg_user_id}')
                return MakeMove(room_exists=False)

            room_data = SnowDuelRoom.model_validate_json(room_data)

            if room_data.game_status != 'in_progress':
                logger.warning(f'Can not make a move because '
                               f'the room {self.hash_name} is in status "{room_data.game_status}"')
                return MakeMove(room_exists=False)

            if tg_user_id == room_data.owner.tg_user_id:
                if room_data.who_moves == WhoMoves.owner:
                    current_player = room_data.owner
                    another_player, who_move_next = room_data.opponent, WhoMoves.opponent
                else:
                    logger.info(f'tg_user_id:{tg_user_id} is not current user move in the room {self.hash_name}')
                    return MakeMove(is_current_user_move=False)

            elif tg_user_id == room_data.opponent.tg_user_id:
                if room_data.who_moves == WhoMoves.opponent:
                    current_player = room_data.opponent
                    another_player, who_move_next = room_data.owner, WhoMoves.owner
                else:
                    logger.info(f'tg_user_id:{tg_user_id} is not current user move in the room {self.hash_name}')
                    return MakeMove(is_current_user_move=False)

            else:
                logger.info(f'tg_user_id:{tg_user_id} not in the room {self.hash_name}')
                return MakeMove(user_in_room=False)

            current_player.moves += 1
            current_player.dttm_last_move = datetime.now()

            is_hit = settings.ConfigSnowDuel.is_hit(current_player.hit_chance)
            if is_hit:
                current_player.points += 1

            if current_player.points >= self.limit_points_to_win:
                room_data.game_status = 'finished'

                async with r.pipeline() as pipe:
                    await pipe.set(self.hash_name, room_data.model_dump_json())
                    await pipe.hincrby(self.user_data_pattern.format(current_player.tg_user_id), 'wins')
                    await pipe.hincrby(self.user_data_pattern.format(another_player.tg_user_id), 'losses')

                    await pipe.execute()

                logger.info('tg_user_id:{} wins tg_user_id:{} in room {}'.format(
                    current_player.tg_user_id, another_player.tg_user_id, self.hash_name))

                return MakeMove(snow_duel_data=room_data, is_hit=is_hit)

            if (room_data.owner.moves + room_data.opponent.moves) % 2 == 0:
                room_data.current_round += 1

            room_data.who_moves = who_move_next

            await r.set(self.hash_name, room_data.model_dump_json())

            logger.info(f'tg_user_id:{tg_user_id} made a move in {self.hash_name} successfully')

            return MakeMove(snow_duel_data=room_data, is_hit=is_hit)

        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.error('Error connecting to Redis while tg_user_id:{} make a move in the room {}: {}'.format(
                tg_user_id, self.hash_name, e
            ))
            raise
        except Exception as e:
            logger.critical('An unexpected error while tg_user_id:{} make a move in the room {}: {}'.format(
                tg_user_id, self.hash_name, e
            ))
            raise
        finally:
            await r.aclose()

    @redis_retry()
    async def cancel_game(self, initiator_tg_user_id: int) -> CancelGame | None:
        logger.info(f'tg_user_id:{initiator_tg_user_id} cancels the game room {self.hash_name}')

        r = await create_redis_client()
        try:
            room_data = await r.get(self.hash_name)

            if room_data is None:
                logger.error(f'Room {self.hash_name} not found for snow_duel for tg_user_id:{initiator_tg_user_id}')
                return

            room_data = SnowDuelRoom.model_validate_json(room_data)

            if room_data.game_status not in ('created', 'in_progress'):
                logger.warning(f'Can not cancel the game because '
                               f'the room {self.hash_name} is in status "{room_data.game_status}"')
                return

            if initiator_tg_user_id == room_data.owner.tg_user_id:
                another_user_id = room_data.opponent.tg_user_id if room_data.opponent else None
            elif room_data.opponent and initiator_tg_user_id == room_data.opponent.tg_user_id:
                another_user_id = room_data.owner.tg_user_id
            else:
                logger.warning(f'tg_user_id:{initiator_tg_user_id} not in the game room {self.hash_name}')
                return

            room_data.game_status = 'cancelled'

            await r.set(self.hash_name, room_data.model_dump_json())

            logger.info(f'tg_user_id:{initiator_tg_user_id} canceled the game room {self.hash_name} successfully')

            return CancelGame(another_user_id=another_user_id, snow_duel_data=room_data)

        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.error('Error connecting to Redis while tg_user_id:{} cancelling the game room {}: {}'.format(
                initiator_tg_user_id, self.hash_name, e
            ))
            raise
        except Exception as e:
            logger.critical('An unexpected error while tg_user_id:{} cancelling the game room {}: {}'.format(
                initiator_tg_user_id, self.hash_name, e
            ))
            raise
        finally:
            await r.aclose()

    async def get_room(self) -> SnowDuelRoom | None:
        logger.info(f'Getting room {self.hash_name}')

        r = await create_redis_client()
        try:
            room_data = await r.get(self.hash_name)

            if room_data is None:
                logger.error(f'Room {self.hash_name} not found for snow_duel')
                return
            return SnowDuelRoom.model_validate_json(room_data)

        except Exception as e:
            logger.error(f"Error while getting room: {e}")
        finally:
            await r.aclose()


async def main() -> None:
    chat_id = 0
    message_id = 0
    ic(await SnowDuelDBQueries(chat_id=chat_id, message_id=message_id).get_room())


if __name__ == "__main__":
    import asyncio
    from icecream import ic

    asyncio.run(main())
