from aiogram.filters import Command
from aiogram.types import Message

from configs import SnowmanFallingChances
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
