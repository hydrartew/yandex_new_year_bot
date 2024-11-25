from random import randint


class SnowmanFallingChances:
    def __init__(self, height_increased: int):
        """
        Конфигурация шансов падения снеговика для игры snowman

        :param height_increased: на сколько сантиметров будет увеличен рост снеговика
        """
        self.height_increased = height_increased
        self.config = [
            {
                'height_increased': 1,
                'percentage_falling_chance': '2%'
            },
            {
                'height_increased': 2,
                'percentage_falling_chance': '4%'
            },
            {
                'height_increased': 3,
                'percentage_falling_chance': '6%'
            },
            {
                'height_increased': 4,
                'percentage_falling_chance': '8%'
            },
            {
                'height_increased': 5,
                'percentage_falling_chance': '10%'
            },
            {
                'height_increased': 6,
                'percentage_falling_chance': '12%'
            },
            {
                'height_increased': 7,
                'percentage_falling_chance': '14%'
            },
            {
                'height_increased': 8,
                'percentage_falling_chance': '16%'
            },
            {
                'height_increased': 9,
                'percentage_falling_chance': '18%'
            },
            {
                'height_increased': 10,
                'percentage_falling_chance': '20%'
            }
        ]

    @property
    def is_fall(self):
        return randint(1, 100) <= int(self.percentage_falling_chance[:-1])

    @property
    def percentage_falling_chance(self):
        return self.config[self.height_increased - 1].get('percentage_falling_chance')
