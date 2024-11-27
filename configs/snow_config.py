import random


class SecretBox:
    def __init__(self):
        """Конфигурация шанса выпадения сюрприз бокса для игры /snow"""
        self.config = {  # TODO: вынести в отдельный json-файл
            "percentage_chance": "0.2%",  # 1/500
            "number_snowballs": {
                "from": 10,
                "to": 100
            }
        }
        self.percentage_chance = self.config["percentage_chance"]

    @property
    def percentage_chance(self) -> float:
        return self.__percentage_chance

    @percentage_chance.setter
    def percentage_chance(self, v: str) -> None:
        self.__percentage_chance = float(v.strip('%')) / 100  # "0.2%" -> 0.002

    @property
    def is_secret_box(self):
        return random.random() < self.percentage_chance

    @property
    def number_snowballs(self):
        return random.randint(self.config["number_snowballs"]["from"], self.config["number_snowballs"]["to"])


secret_box = SecretBox()
