import asyncio
import logging

from aiogram import Router, Dispatcher, Bot, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram_i18n import I18nContext, I18nMiddleware, LazyProxy
from aiogram_i18n.cores import FluentRuntimeCore
from aiogram_i18n.types import InlineKeyboardButton
from aiogram_i18n.utils.language_inline_keyboard import LanguageInlineMarkup

from configs import settings
from loader import storage

router = Router()

lang_kb = LanguageInlineMarkup(key="lang_button", keyboard=[
    [InlineKeyboardButton(text=LazyProxy("back"), callback_data="back")]
])


@router.message(CommandStart())
async def cmd_start(message: Message, i18n: I18nContext):
    await message.answer(text=i18n.get("hello", user=message.from_user.full_name))


@router.callback_query(F.data == "back")
async def btn_help(call: CallbackQuery, i18n: I18nContext):
    await call.message.edit_text(
        text=i18n.get("hello", user=call.from_user.full_name)
    )


@router.callback_query(lang_kb.filter)
async def btn_help(call: CallbackQuery, lang: str, i18n: I18nContext):
    await i18n.set_locale(locale=lang)  # TODO: перенести в фильтры
    await call.message.edit_text(text=i18n.cur.lang(language=i18n.locale))


@router.message(Command("lang"))
async def cmd_lang(message: Message, i18n: I18nContext):
    await message.reply(
        text=i18n.get("cur-lang", language=i18n.locale), reply_markup=lang_kb.reply_markup()
    )


async def main():
    logging.basicConfig(level=logging.INFO)

    dp = Dispatcher(storage=storage)

    bot = Bot(settings.TELEGRAM_BOT_TOKEN.get_secret_value(),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    mw = I18nMiddleware(
        core=FluentRuntimeCore(
            path="locales/{locale}/LC_MESSAGES",
        ),
    )
    dp.include_router(router)
    mw.setup(dispatcher=dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
