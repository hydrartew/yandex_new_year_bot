import json

import requests
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_i18n import I18nContext

from configs import settings
from db.db_redis import get_user_stats
from filters import GroupChat, IsSubscribed
from handlers import dp
from localization import Localization

from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log
import logging

from schemas import GiveAchievement, ResponseGiveAchievement

logger = logging.getLogger(__name__)


@dp.message(Command('night_king'), GroupChat(), IsSubscribed(), flags={"throttling_key": "night_king"})
async def night_king(message: Message, i18n: I18nContext) -> None:
    """Скрытая команда для получения ачивки"""
    localization = Localization(message, i18n)

    logger.info('/night_king tg_user_id:{}, start of command processing'.format(message.from_user.id))

    user_stats = await get_user_stats(message.from_user.id)

    if user_stats.losses < settings.NIGHT_KING_LOSS_THRESHOLD_TO_GET_ACHIEVEMENT:
        logger.info(
            'The achievement is not available yet for tg_user_id:{}, as the threshold:{} has not been crossed.'
            .format(message.from_user.id, user_stats.losses)
        )
        await message.reply(localization.get('night-king-unavailable'))

    else:
        achievement = Achievement(message.from_user.username)
        data = achievement.give()

        fill_out_the_form = 'заполни <a href="{}">форму</a>'.format(settings.YANDEX_FORM_FEEDBACK_LINK)

        if data.invalid_tg_username:
            await message.reply(
                'Твой логин в телеграм не совпадает с логином на Стаффе. Актуализируй телеграм логин на Стаффе и {}'
                .format(fill_out_the_form)
            )

        elif data.already_given:
            await message.reply(localization.get('night-king-already-given'))

        elif data.error_occurred:
            await message.reply(
                'Произошла ошибка при выдачи секретной ачивки, попробуй позже или {}'.format(fill_out_the_form)
            )

        else:
            await message.reply(localization.get('night-king-unblocked'))

    logger.info('/night_king tg_user_id:{}, end of command processing'.format(message.from_user.id))


class Achievement:
    def __init__(self, tg_username: str):
        self.tg_username = tg_username
        self.achievement_id = 15401

        self.API = 'https://staff.yandex-team.ru/api/achievery/'
        self.headers = {
            'Authorization': f'OAuth {settings.TRACKER_BOT_INTERNAL_TOKEN.get_secret_value()}',
            'Content-Type': 'application/json'
        }

        self.json_file = f'{settings.static_json_path}mapping_tg_to_staff.json'

    @property
    def _staff_login(self) -> str | None:
        try:
            with open(self.json_file, "r+", encoding='utf-8') as f:
                mapping_tg_to_staff = json.load(f)
            return mapping_tg_to_staff.get(self.tg_username)
        except FileNotFoundError:
            logger.error(f'File {self.json_file} not found:')
            raise
        except json.JSONDecodeError:
            logger.error("Error decoding JSON from the mapping file.")
            raise

    @retry(
        stop=stop_after_attempt(7),
        wait=wait_exponential(min=1, max=5),
        before_sleep=before_sleep_log(logger, logging.INFO)
    )
    def give(self) -> ResponseGiveAchievement:
        return ResponseGiveAchievement(error_occurred=True)  # костыль hot fix для правок бизнес логики выдачи ачивки
        staff_login = self._staff_login
        if staff_login is None:
            logger.warning('tg_username:{} has no staff'.format(self.tg_username))
            return ResponseGiveAchievement(invalid_tg_username=True)

        data = GiveAchievement(
            achievement_id=self.achievement_id,
            staff_login=staff_login
        )

        logger.info('Try to give achievement {}'.format(repr(data)))

        response = requests.post(
            self.API + 'given/',
            headers=self.headers,
            json=data.model_dump(by_alias=True)
        )

        if response.ok:
            logger.info('The achievement {} was given successfully'.format(repr(data)))
            return ResponseGiveAchievement(given_successfully=True)

        if response.status_code == 403:
            logger.error('Access denied. Check your token.')
            return ResponseGiveAchievement(error_occurred=True)

        if response.status_code == 409 and hasattr(response, 'json'):
            list_errors = response.json().get('errors', [])
            if list_errors != 0:
                for i in range(len(list_errors)):
                    if list_errors[i].get('code') == 'duplicate_entry':
                        logger.info('The achievement {} was already given'.format(repr(data)))
                        return ResponseGiveAchievement(already_given=True)
                    if list_errors[i].get('code') == 'unacceptable_level':
                        logger.error(
                            'Requested level is not available for that Achievement: {} '.format(repr(data))
                        )
                        return ResponseGiveAchievement(error_occurred=True)
        try:
            response.raise_for_status()
        except:
            logger.error('Error given achievement {}: {}'.format(repr(data), response.text))
            raise

        return ResponseGiveAchievement(error_occurred=True)
