import os

# Токен бота
MAX_BOT_TOKEN = os.getenv("MAX_BOT_TOKEN")

# Базовый URL API MAX
MAX_API_BASE = "https://platform-api.max.ru"

# Вебхук URL (только если используем Webhook)
RENDER_DOMAIN = os.getenv("RENDER_EXTERNAL_URL", "")
WEBHOOK_URL = f"{RENDER_DOMAIN}/webhook" if RENDER_DOMAIN else None
