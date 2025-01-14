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

logger = logging.getLogger(__name__)


class IsSubscribed(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery, bot: Bot, i18n: I18nContext) -> bool:
        localization = Localization(message, i18n)

        if isinstance(message, CallbackQuery):
            message = message.message

        if settings.CHAT_IDS_WHITE_LIST is not None and len(settings.CHAT_IDS_WHITE_LIST) != 0:
            if message.chat.id not in settings.CHAT_IDS_WHITE_LIST:
                return False

        if settings.CHAT_IDS_BLACK_LIST is not None and len(settings.CHAT_IDS_BLACK_LIST) != 0:
            if message.chat.id in settings.CHAT_IDS_BLACK_LIST:
                return False

        if settings.TELEGRAM_CHANNEL_BOT_NEWS_CHAT_ID is None:
            return True

        sub = await bot.get_chat_member(
            chat_id=settings.TELEGRAM_CHANNEL_BOT_NEWS_CHAT_ID,
            user_id=message.from_user.id
        )

        if sub.status in (ChatMemberStatus.KICKED, ChatMemberStatus.RESTRICTED):
            return False

        if sub.status == ChatMemberStatus.LEFT:
            logger.info(
                'tg_user_id:{} - new user w/o subscribe, chat_id:{}'.format(message.from_user.id, message.chat.id)
            )
            if isinstance(message, Message):
                try:
                    await message.reply(
                        localization.get(
                            'sub-msg',
                            TELEGRAM_CHANNEL_BOT_NEWS_INVITE_HYPERLINK=
                            settings.TELEGRAM_CHANNEL_BOT_NEWS_INVITE_HYPERLINK
                        ),
                        reply_markup=ikb_subscription(localization),
                        disable_web_page_preview=True
                    )
                except TelegramForbiddenError:
                    logger.warning(
                        'The message could not be sent because bot was blocked by the tg_user_id:{}'
                        .format(message.from_user.id)
                    )

            else:
                await message.answer(
                    localization.get('sub-alert'),
                    show_alert=True,
                    cache_time=10
                )
            return False

        return True


class IsBlocked(BaseFilter):
    def __init__(self, user_in_fsm_state: bool = False):
        self.bad_statuses = [ChatMemberStatus.KICKED, ChatMemberStatus.RESTRICTED]

        # для случая, когда пользователь находится в состоянии FSMContext, и сам вышел из группы
        if user_in_fsm_state:
            self.bad_statuses.append(ChatMemberStatus.LEFT)

    async def __call__(self, message: Message, bot: Bot) -> bool:
        sub = await bot.get_chat_member(
            chat_id=settings.TELEGRAM_CHANNEL_BOT_NEWS_CHAT_ID,
            user_id=message.from_user.id
        )
        if sub.status in self.bad_statuses:
            return False
        return True
