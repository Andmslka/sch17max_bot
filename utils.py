import requests
import logging
from config import MAX_BOT_TOKEN, MAX_API_BASE

logger = logging.getLogger(__name__)

HEADERS = {"Authorization": MAX_BOT_TOKEN, "Content-Type": "application/json"}

def get_bot_info():
    """Получить информацию о боте"""
    if not MAX_BOT_TOKEN:
        logger.error("MAX_BOT_TOKEN не настроен")
        return {}

    try:
        r = requests.get(f"{MAX_API_BASE}/me", headers=HEADERS, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Ошибка получения информации о боте: {e}")
        return {}

def send_message(chat_id: int, text: str, format_type: str = "Markdown"):
    """Отправить сообщение в чат"""
    if not MAX_BOT_TOKEN:
        logger.error("MAX_BOT_TOKEN не настроен")
        return False

    payload = {
        "chat_id": chat_id,
        "text": text,
        "format": format_type
    }

    try:
        r = requests.post(f"{MAX_API_BASE}/messages", headers=HEADERS, json=payload, timeout=10)
        r.raise_for_status()
        logger.info(f"Сообщение отправлено в чат {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        return False

def register_webhook(url: str, update_types=None):
    """Зарегистрировать Webhook на MAX"""
    if not update_types:
        update_types = ["bot_started", "message_created", "message_callback"]

    payload = {"url": url, "update_types": update_types}

    try:
        r = requests.post(f"{MAX_API_BASE}/subscriptions", headers=HEADERS, json=payload, timeout=10)
        r.raise_for_status()
        logger.info(f"Webhook зарегистрирован: {url}")
        return True
    except Exception as e:
        logger.error(f"Ошибка регистрации webhook: {e}")
        return False
