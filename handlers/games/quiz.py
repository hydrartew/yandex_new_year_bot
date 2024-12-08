from aiogram.filters import Command
from aiogram.types import Message

from configs import settings
from filters import GroupChat, IsSubscribed
from loader import dp


@dp.message(Command('quiz'), GroupChat(), IsSubscribed(), flags={"throttling_key": "quiz"})
async def game_quiz(message: Message) -> None:
    await message.reply(
        'Игра пока недоступна, следи за обновлениями в телеграм канале <a href="{}">{}</a>'.format(
            settings.TELEGRAM_CHANNEL_BOT_NEWS_INVITE_LINK, settings.TELEGRAM_CHANNEL_BOT_NEWS_NAME
        )
    )
