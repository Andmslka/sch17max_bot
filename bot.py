import os
import logging
import requests
from flask import Flask, request, jsonify

def get_chat_id(update):
    # Сначала пытаемся взять chat_id на верхнем уровне
    if update.get("chat_id"):
        return update["chat_id"]
    # Если нет, ищем внутри message -> recipient
    if "message" in update and "recipient" in update["message"]:
        return update["message"]["recipient"].get("chat_id")
    # fallback: None
    return None

def get_message_text(update):
    # Сначала проверяем поле text на верхнем уровне
    if update.get("text"):
        return update["text"]
    # Ищем внутри message -> body -> text
    if "message" in update and "body" in update["message"]:
        return update["message"]["body"].get("text")
    return None
    
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
    logger.info("=== Новый апдейт ===")
    logger.info(json.dumps(update, indent=4, ensure_ascii=False))

    chat_id = get_chat_id(update)
    text = get_message_text(update)

    logger.info(f"Определён chat_id: {chat_id}")
    logger.info(f"Текст сообщения: {text}")

    # здесь можно вызывать функцию отправки сообщения
    if chat_id and text:
        send_message(chat_id, f"Вы написали: {text}")

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
