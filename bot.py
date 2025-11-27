import logging
from flask import Flask, request, jsonify
from config import WEBHOOK_URL
from utils import get_bot_info, send_message, register_webhook

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    """Обработчик событий от MAX через Webhook"""
    data = request.json
    if not data:
        return jsonify({"status": "empty payload"}), 400

    update_type = data.get("update_type")
    chat_id = data.get("chat_id")
    payload = data.get("payload")

    logging.info(f"Update received: {update_type}, chat_id: {chat_id}, payload: {payload}")

    if update_type == "bot_started":
        if chat_id:
            send_message(chat_id, f"Привет! Вы запустили бота. Payload: {payload}")
        else:
            logging.warning("chat_id отсутствует в bot_started")

    if update_type == "message_created":
        if chat_id:
            text = data.get("text", "")
            send_message(chat_id, f"Вы написали: {text}")
        else:
            logging.warning("chat_id отсутствует в message_created")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    if WEBHOOK_URL:
        register_webhook(WEBHOOK_URL)
        logging.info(f"Webhook URL: {WEBHOOK_URL} зарегистрирован")
    logging.info(f"Bot info: {get_bot_info()}")
    app.run(host="0.0.0.0", port=5000)
