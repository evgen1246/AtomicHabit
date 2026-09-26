import requests
from django.conf import settings


class TelegramService:
    """Сервис для отправки сообщений через Telegram"""

    @staticmethod
    def send_message(chat_id: str, text: str) -> dict:
        """Отправляет сообщение пользователю в Telegram."""

        if not settings.TELEGRAM_BOT_TOKEN:
            return {"ok": False, "error": "Telegram token не задан"}

        if not chat_id:
            return {"ok": False, "error": "Не указан chat_id"}

        url = f"{settings.TELEGRAM_API_URL}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.json()
        except requests.RequestException as e:
            return {"ok": False, "error": str(e)}
