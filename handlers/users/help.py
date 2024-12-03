from aiogram.filters import Command
from aiogram.types import Message

from filters import GroupChat, PrivateChat
from keyboards.inline import ikb_welcome_private_chat, ikb_welcome_group_chat
from loader import dp

help_text = """
Я новогодний бот для сотрудников Яндекса 🎅

Новостной канал бота - <a href="https://nda.ya.ru/t/8Ve9IRKc79adW7">YNYB News</a>

Баг, фичреквест или что-то ещё - заполняй <a href="https://forms.yandex-team.ru/ext/surveys/13711111/">форму</a>

<b>🎲 Игры</b>

<blockquote>❄️ <b>Снежный денёк</b> /snow</blockquote>
<i>Отправь команду в ответ на сообщение того, в кого хочешь бросить снежок</i>

<blockquote>❄️🔫 <b>Снежная дуэль</b> /snow_duel</blockquote>
<i>1️⃣ Расстояние между оппонентами определяется случайно (от 25 до 45 шагов), чем больше расстояние, тем меньше шансов на попадание
2️⃣ Право первого выстрела определяется в случайном порядке 50/50
3️⃣ Чем больше дуэлей сыграно, тем больше опыта. Это увеличивает твой шанс попадения в противника. (Текущий бонус можно посмотреть в /stats)
4️⃣ Игра длится до 2-х попаданий</i>

<blockquote>☃️ <b>Снеговичок</b> /snowman</blockquote>
<i>Цель игры слепить самого высокого снеговика. Но будьте аккуратный, он может упасть.</i>

<blockquote>🔮 <b>Предсказания</b>  /prediction</blockquote>
<i>Можно использовать 1 раз в 12ч (ты можешь написать свое через <a href="https://forms.yandex-team.ru/ext/surveys/13711111/">форму</a>, оно случайно выпадет кому-то)</i>
"""


@dp.message(Command('help', 'start'), PrivateChat())
async def welcome_private_chat(message: Message) -> None:
    global help_text

    text = (
        '{}\n⚠️ В лс отвечаю только на команды /help и /stats\n\n'
        '✅ Чтобы начать пользоваться мной, добавь меня в группу'
    ).format(help_text)

    if message.text == '/start':
        text = 'Привет 👋\n{}'.format(text)

    await message.answer(text, reply_markup=ikb_welcome_private_chat)


@dp.message(Command('help', 'start'), GroupChat())
async def welcome_group_chat(message: Message) -> None:
    global help_text
    await message.answer(help_text, reply_markup=ikb_welcome_group_chat)
