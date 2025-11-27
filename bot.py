import os
import logging
import requests
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_BOT_TOKEN = os.environ.get("MAX_BOT_TOKEN")  # токен из Render
MAX_API_URL = "https://platform-api.max.ru/messages"

app = Flask(__name__)

# Универсальная функция для извлечения chat_id
def get_chat_id(update):
    if update.get("chat_id"):
        return update["chat_id"]
    if update.get("message") and update["message"].get("chat") and update["message"]["chat"].get("id"):
        return update["message"]["chat"]["id"]
    if update.get("user") and update["user"].get("user_id"):
        return update["user"]["user_id"]
    return None

# Функция отправки сообщений
def send_message(chat_id, text):
    if not chat_id:
        logger.warning("chat_id отсутствует, сообщение не отправлено")
        return
    headers = {"Authorization": MAX_BOT_TOKEN, "Content-Type": "application/json"}
    payload = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(MAX_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        logger.info(f"Сообщение отправлено в чат {chat_id}")
    except requests.HTTPError as e:
        logger.error(f"Ошибка отправки сообщения: {e}")

# Обработчик вебхука
@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.json
    logger.info(f"Update received: {update.get('update_type')}, chat_id: {get_chat_id(update)}, payload: {update.get('payload')}")

    chat_id = get_chat_id(update)
    
    # Универсальные ответы
    if update.get("update_type") == "bot_started":
        send_message(chat_id, f"Привет! Вы запустили бота. Payload: {update.get('payload')}")
    elif update.get("update_type") == "message_created":
        message_text = update.get("message", {}).get("text", "")
        send_message(chat_id, f"Вы написали: {message_text}")
    else:
        send_message(chat_id, f"Получено событие {update.get('update_type')}")

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
