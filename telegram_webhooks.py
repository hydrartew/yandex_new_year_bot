import requests

from config import settings


def send_message(chat_id: int | str, text: str, reply_to_message_id: int | None = None,
                 bot_token: str = settings.TELEGRAM_BOT_TOKEN) -> dict:
    return requests.post(
        url=f'https://api.telegram.org/bot{bot_token}/sendMessage',
        params={
            "chat_id": int(chat_id),
            "text": text,
            "reply_to_message_id": reply_to_message_id,
            "parse_mode": "HTML"
        },
        headers={
            'Content-Type': 'application/json'
        }
    ).json()


print(send_message(-1002137483542, '@hydrartew увеличил рост снеговичка ☃️ на 5см'))
