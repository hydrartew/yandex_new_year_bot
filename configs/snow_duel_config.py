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


snow_duel_config = SnowDuelConfig()
