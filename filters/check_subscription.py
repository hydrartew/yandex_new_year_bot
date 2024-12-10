import logging

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from aiogram_i18n import I18nContext

from configs import settings
from keyboards.inline import ikb_subscription
from localization import Localization

logger = logging.getLogger('handlers')


class IsSubscribed(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery, bot: Bot, i18n: I18nContext) -> bool:
        localization = Localization(message, i18n)

        sub = await bot.get_chat_member(
            chat_id=settings.TELEGRAM_CHANNEL_BOT_NEWS_CHAT_ID,
            user_id=message.from_user.id
        )

        if sub.status in (ChatMemberStatus.KICKED, ChatMemberStatus.RESTRICTED):
            return False

        if sub.status == ChatMemberStatus.LEFT:
            if isinstance(message, Message):
                try:
                    await message.reply(
                        localization.get('sub-msg', channel=settings.TELEGRAM_CHANNEL_BOT_NEWS_INVITE_HYPERLINK),
                        reply_markup=ikb_subscription
                    )
                except TelegramForbiddenError:
                    logger.warning(
                        'The message could not be sent because bot was blocked by the tg_user_id:{}'
                        .format(message.from_user.id)
                    )

            else:
                await message.answer(
                    localization.get('sub-alert', channel=settings.TELEGRAM_CHANNEL_BOT_NEWS_NAME),
                    show_alert=True,
                    cache_time=10
                )
            return False

        return True


class IsBlocked(BaseFilter):
    async def __call__(self, message: Message, bot: Bot) -> bool:
        sub = await bot.get_chat_member(
            chat_id=settings.TELEGRAM_CHANNEL_BOT_NEWS_CHAT_ID,
            user_id=message.from_user.id
        )
        if sub.status in (ChatMemberStatus.KICKED, ChatMemberStatus.RESTRICTED):
            return False
        return True
