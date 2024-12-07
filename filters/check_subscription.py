from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.filters import BaseFilter
from aiogram.types import Message

from keyboards.inline import ikb_subscription


class IsSubscribed(BaseFilter):
    async def __call__(self, message: Message, bot: Bot) -> bool:
        sub = await bot.get_chat_member(chat_id=-1002015280712, user_id=message.from_user.id)

        if sub.status in (ChatMemberStatus.KICKED, ChatMemberStatus.RESTRICTED):
            return False

        if sub.status == ChatMemberStatus.LEFT:
            await message.reply(
                'Для участия в новогоднем ивенте ✨ нужно подписаться на канал '
                '<a href="https://nda.ya.ru/t/8Ve9IRKc79adW7">YNYB News</a>',
                reply_markup=ikb_subscription
            )
            return False

        return True
