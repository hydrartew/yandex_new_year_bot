import asyncio

from icecream import ic
from pydantic import BaseModel
from telethon import TelegramClient
from telethon.errors import ChatAdminRequiredError, UserNotParticipantError, ChannelPrivateError, ChatIdInvalidError

from configs import settings

api_id = settings.TELEGRAM_API_ID
api_hash = settings.TELEGRAM_API_HASH

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=settings.TELEGRAM_BOT_TOKEN.get_secret_value())


class TelegramUser(BaseModel):
    id: int
    username: str | None
    first_name: str
    last_name: str | None
    bot: bool
    deleted: bool


async def check_chat_exists(client, group_id) -> bool:
    try:
        await client.get_entity(group_id)
        return True
    except (ValueError, IndexError, ChatAdminRequiredError, UserNotParticipantError,
            ChannelPrivateError, ChatIdInvalidError):
        return False


async def get_chat_users(client, group_id):
    if not await check_chat_exists(client, group_id):
        raise ValueError('Chat {} does not exist'.format(group_id))
    async for user in client.iter_participants(group_id):
        telegram_user = TelegramUser(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            bot=user.bot,
            deleted=user.deleted,
        )
        ic(telegram_user)


async def main():
    group_id = -1002015280712
    await get_chat_users(bot, group_id)

if __name__ == '__main__':
    with bot:
        asyncio.get_event_loop().run_until_complete(main())
