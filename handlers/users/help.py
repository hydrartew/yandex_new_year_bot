from aiogram.filters import Command
from aiogram.types import Message

from filters import GroupChat, PrivateChat
from keyboards.inline import ikb_welcome_private_chat, ikb_welcome_group_chat
from loader import dp

help_text = """
Я новогодний бот для сотрудников Яндекса 🎅

<b>Предсказания</b> 🔮, баг, фичреквест или что-то ещё - заполняй <a href="https://forms.yandex-team.ru/ext/surveys/13711111/">форму</a>

Новостной канал бота YNYB News: https://nda.ya.ru/t/8Ve9IRKc79adW7

<b>=Игры=</b>

/snow - <b>Снежный денёк</b>: отправь команду в ответ на сообщение того, в кого хочешь бросить снежок;

/snow_duel - <b>Снежная дуэль</b>: 
1️⃣ расстояние между оппонентами определяется рандомно от 25 до 45 шагов: чем больше расстояние, тем меньше шансов на попадание;
2️⃣ право первого выстрела определяется рандомно 50/50;
3️⃣ чем больше дуэлей сыграно, тем больше опыта => шанс попадания увеличивается и прибавляется к шансу в п.1 (текущий бафф можно посмотреть в /stats);
4️⃣ игра до 2 попаданий

/snowman - <b>Снеговичок</b>: цель игры слепить самого высокого снеговика

/prediction - <b>Новогодние предсказания</b>: можно использовать 1 раз в 12ч, ты можешь написать свое предсказание через <a href="https://forms.yandex-team.ru/ext/surveys/13711111/">форму</a>, оно рандомно выпадет кому-то
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
