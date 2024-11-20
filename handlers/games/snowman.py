from aiogram.filters import Command
from aiogram.types import Message

from random import randint

from db.db_redis import update_snowman
from filters import GroupChat
from handlers import dp


@dp.message(Command('snowman'), GroupChat())
async def game_snowman(message: Message) -> None:
    list_text = message.text.split()
    if len(list_text) != 2 or not list_text[1].isdigit() or int(list_text[1]) > 10 or int(list_text[1]) < 1:
        await message.reply(
            'Укажи число от 1 до 10, на сколько сантиметров нужно увеличить рост снеговичка ☃️\n\n'
            'Пример: <code>/snowman 8</code>\n\n'
            'Чем больше число, тем выше шанс, что снеговичок ☃️ упадет'
        )
        return

    height_increased = int(list_text[1])
    snowman_fall = SnowmanFallingChances(height_increased)

    text = f'@{message.from_user.username} увеличил(а) рост снеговичка ☃️ на {height_increased} см'
    if snowman_fall.is_fall:
        await message.answer(text=text + f', и он упал 🫠 '
                                         f'(шанс падения: {snowman_fall.percentage_falling_chance})')
        await update_snowman(message.from_user.id, -1)
        return

    snowman = await update_snowman(message.from_user.id, height_increased)
    await message.answer(text=text + f'\nТекущий рост: {snowman.current} см')


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
