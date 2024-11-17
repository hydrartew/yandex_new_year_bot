from aiogram.enums.chat_type import ChatType
from aiogram.filters import Command
from aiogram.types import Message

from loader import dp


@dp.message(Command('help', 'start'))
async def command_start_handler(message: Message) -> None:
    text = (f'Я новогодний бот для сотрудников Яндекса 🎅\n\n'
            f'Вся информация обо мне/играх/командах (и не только) есть на '
            f'<a href="https://wiki.yandex-team.ru/">Wiki</a> ℹ️ \n\n'
            f'<b>Предсказания</b> 🔮, баг, фичреквест или что-то ещё - заполняй '
            f'<a href="https://forms.yandex-team.ru/ext/surveys/13711111/">форму</a>')

    if message.text == '/start':
        text = 'Привет 👋 ' + text

    if message.chat.type == ChatType.PRIVATE:
        text += (f'\n\nВ лс отвечаю только на команды /help и /profile\n\n'
                 f'Чтобы начать пользоваться мной, добавь меня в группу ✅\n\n')

    await message.answer(text)
