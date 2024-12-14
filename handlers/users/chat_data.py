from datetime import datetime, timezone

from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import ChatMemberUpdated

from db.db_ydb import upsert_chat_data
from filters import IsBlocked, GroupChat, ChannelChat
from loader import dp
from schemas import ChatMemberUpdatedData


@dp.my_chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER), IsBlocked())
@dp.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER), GroupChat() or ChannelChat(), IsBlocked())
# Для приватного чата событие "chat open", т.е. ввод команды /start, отлавливается в filters.chat_type.PrivateChat
async def update_chat_data(event: ChatMemberUpdated):
    await upsert_chat_data(
        ChatMemberUpdatedData(
            chat_id=event.chat.id,
            type=event.chat.type,
            title=event.chat.title,
            from_user_id=event.from_user.id,
            from_user_username=event.from_user.username,
            from_user_language_code=event.from_user.language_code,
            chat_member_status=event.new_chat_member.status,
            utc_dttm_action=datetime.now(timezone.utc)
        )
    )
