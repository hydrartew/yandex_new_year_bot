import random

from schemas import WhoMoves


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
            },
            "user_buff": {
                "interval_of_games_played": 20,
                "increase_hit_chance": "1%",
                "max_increase_hit_chance": "15%"
            }
        }

    def get_random_distance(self) -> int:
        _config = self.config['distance']
        return random.randint(_config['bottom_bound']['steps'], _config['upper_bound']['steps'])

    def hit_chance(self, distance: int) -> float:
        _config = self.config['distance']

        upper_steps = _config['upper_bound']['steps']
        bottom_steps = _config['bottom_bound']['steps']

        if not (bottom_steps <= distance <= upper_steps):
            raise ValueError(f"Steps must be between distance.bottom_bound.steps:{bottom_steps} "
                             f"and distance.upper_bound.steps:{upper_steps}")

        bottom_hit_chance = int(_config['bottom_bound']['hit_chance'].strip('%'))
        upper_hit_chance = int(_config['upper_bound']['hit_chance'].strip('%'))

        chance_1_step = (bottom_hit_chance - upper_hit_chance) / (upper_steps - bottom_steps)

        current_step_hit_chance = bottom_hit_chance - ((distance - bottom_steps) * chance_1_step)

        return round(current_step_hit_chance, 2)

    @staticmethod
    def is_hit(hit_chance: float) -> bool:
        return random.choices([
            True,
            False
        ], weights=[
            hit_chance,
            100-hit_chance
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

    def user_buff(self, games_played: int) -> float:
        _config = self.config['user_buff']

        buff = (games_played // _config['interval_of_games_played']) * float(_config['increase_hit_chance'].strip('%'))

        max_increase_hit_chance = float(_config['max_increase_hit_chance'].strip('%'))
        if buff > max_increase_hit_chance:
            return max_increase_hit_chance
        return buff


snow_duel_config = SnowDuelConfig()
