import logging

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from keyboards.inline import ikb_subscription

logger = logging.getLogger('handlers')


class IsSubscribed(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery, bot: Bot) -> bool:
        sub = await bot.get_chat_member(chat_id=-1002015280712, user_id=message.from_user.id)

        if sub.status in (ChatMemberStatus.KICKED, ChatMemberStatus.RESTRICTED):
            return False

        if sub.status == ChatMemberStatus.LEFT:
            if isinstance(message, Message):
                try:
                    await message.reply(
                        'Для участия в новогоднем ивенте ✨ нужно подписаться на канал '
                        '<a href="https://nda.ya.ru/t/8Ve9IRKc79adW7">YNYB News</a>',
                        reply_markup=ikb_subscription
                    )
                except TelegramForbiddenError:
                    logger.warning('Bot was blocked by the tg_user_id:{}'.format(message.from_user.id))

            else:
                await message.answer(
                    'Для участия в новогоднем ивенте ✨ нужно подписаться на канал YNYB News, '
                    'вызови любую команду, там будет ссылка',
                    show_alert=True,
                    cache_time=10
                )
            return False

        return True


class IsBlocked(BaseFilter):
    async def __call__(self, message: Message, bot: Bot) -> bool:
        sub = await bot.get_chat_member(chat_id=-1002015280712, user_id=message.from_user.id)
        if sub.status in (ChatMemberStatus.KICKED, ChatMemberStatus.RESTRICTED):
            return False
        return True
