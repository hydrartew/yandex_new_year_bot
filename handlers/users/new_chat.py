from datetime import datetime, timezone

from aiogram.enums import ChatMemberStatus
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import ChatMemberUpdated

from loader import dp
from schemas import ChatMemberUpdatedData


@dp.my_chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
@dp.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def welcome_bot(event: ChatMemberUpdated):
    data = ChatMemberUpdatedData(
        chat_id=event.chat.id,
        type=event.chat.type,
        title=event.chat.title,
        from_user_id=event.from_user.id,
        from_user_username=event.from_user.username,
        action='join' if event.new_chat_member.status == ChatMemberStatus.MEMBER else 'block',
        dttm_action=datetime.now(timezone.utc)
    )
    print(data)
    # TODO: запрос в БД
