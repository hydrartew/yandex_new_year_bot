import logging
from datetime import datetime, timezone

from aiogram.enums import ChatType, ChatMemberStatus
from aiogram.filters import BaseFilter
from aiogram.types import Message

from db.db_ydb import upsert_chat_data
from schemas import ChatMemberUpdatedData

logger = logging.getLogger('handlers')


class PrivateChat(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.chat.type != ChatType.PRIVATE:
            return False

        logger.info('tg_user_id:{} in private chat send message: "{}"'.format(message.from_user.id, message.text))

        if message.text == '/start':
            await upsert_chat_data(
                ChatMemberUpdatedData(
                    chat_id=message.chat.id,
                    type=ChatType.PRIVATE,
                    title=message.chat.title,
                    from_user_id=message.from_user.id,
                    from_user_username=message.from_user.username,
                    from_user_language_code=message.from_user.language_code,
                    chat_member_status=ChatMemberStatus.MEMBER,
                    utc_dttm_action=datetime.now(timezone.utc)
                )
            )

        return True


class GroupChat(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)


class GroupAndChannelChat(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL)
