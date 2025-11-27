import os
import logging
import requests
import json
from flask import Flask, request, jsonify

# ========================
# Настройка логирования
# ========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================
# Конфигурация
# ========================
MAX_BOT_TOKEN = os.environ.get("MAX_BOT_TOKEN")  # токен из Render
MAX_API_URL = "https://platform-api.max.ru/messages"

app = Flask(__name__)

# ========================
# Вспомогательные функции
# ========================
def get_chat_id(update):
    """Извлекает chat_id или user_id из апдейта"""
    if "message" in update:
        # Попытка получить chat_id чата
        recipient = update["message"].get("recipient")
        if recipient and recipient.get("chat_id"):
            return recipient["chat_id"], "chat_id"

        # Если чата нет, используем user_id отправителя
        sender = update["message"].get("sender")
        if sender and sender.get("user_id"):
            return sender["user_id"], "user_id"
    return None, None

def get_message_text(update):
    """Извлекает текст сообщения"""
    if "message" in update:
        body = update["message"].get("body")
        if body and body.get("text"):
            return body["text"]
    return None

def send_message(recipient_id, text, recipient_type="chat_id"):
    """Отправка сообщения пользователю или чату через MAX API"""
    if not recipient_id:
        logger.warning("recipient_id отсутствует, сообщение не отправлено")
        return

    headers = {
        "Authorization": MAX_BOT_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text
    }

    params = {recipient_type: recipient_id}

    try:
        response = requests.post(MAX_API_URL, headers=headers, json=payload, params=params)
        response.raise_for_status()
        logger.info(f"Сообщение отправлено ({recipient_type}: {recipient_id})")
    except requests.HTTPError as e:
        logger.error(f"Ошибка отправки сообщения: {e}")
        if e.response is not None:
            logger.error(f"Ответ сервера: {e.response.text}")

# ========================
# Обработчик вебхука
# ========================
@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.json
    logger.info("=== Новый апдейт ===")
    logger.info(json.dumps(update, indent=4, ensure_ascii=False))

    chat_or_user_id, recipient_type = get_chat_id(update)
    text = get_message_text(update)

    logger.info(f"Определён {recipient_type}: {chat_or_user_id}")
    logger.info(f"Текст сообщения: {text}")

    # Ответ пользователю/чату
    if chat_or_user_id and text:
        send_message(chat_or_user_id, f"Вы написали: {text}", recipient_type)

    return jsonify({"status": "ok"})

# ========================
# Запуск приложения
# ========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
