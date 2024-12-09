from aiogram.filters import Command
from aiogram.types import Message
from aiogram_i18n import I18nContext

from configs import settings
from filters import GroupChat, IsSubscribed
from loader import dp
from localization import Localization


@dp.message(Command('quiz'), GroupChat(), IsSubscribed(), flags={"throttling_key": "quiz"})
async def game_quiz(message: Message, i18n: I18nContext) -> None:
    await message.reply(text=Localization(message, i18n).get(
            'quiz', TELEGRAM_CHANNEL_BOT_NEWS_INVITE_HYPERLINK=settings.TELEGRAM_CHANNEL_BOT_NEWS_INVITE_HYPERLINK
        )
    )
