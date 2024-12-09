from typing import Any

from aiogram.types import Message, CallbackQuery
from aiogram_i18n import I18nContext


class Localization:
    def __init__(self, message: Message | CallbackQuery, i18n: I18nContext):
        self.language_code = message.from_user.language_code

        if self.language_code not in i18n.core.available_locales:
            self.language_code = i18n.core.default_locale

        self.i18n = i18n

    def get(self, key: str, /, **kwargs: Any) -> str:
        return self.i18n.get(key, self.language_code, **kwargs)
