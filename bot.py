import os
import requests
import telebot
from flask import Flask, request

# --- Настройки (берутся из переменных окружения) ---
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN")
WEBHOOK_URL      = os.environ.get("WEBHOOK_URL")  # например: https://my-gpt-bot.onrender.com

if not OPENAI_API_KEY or not TELEGRAM_TOKEN:
    raise RuntimeError("Требуются переменные окружения OPENAI_API_KEY и TELEGRAM_TOKEN")

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = Flask(__name__)

# --- Вызов OpenAI через HTTP (requests) ---
def generate_openai_reply(user_text: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",              # если у тебя другой доступный — подставь
        "messages": [{"role": "user", "content": user_text}],
        "max_tokens": 512,
        "temperature": 0.7
    }
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    if not r.ok:
        # Верни понятный текст ошибки
        return f"OpenAI error {r.status_code}: {r.text}"
    data = r.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        return str(data)

# --- Логика бота (ответ всем текстовым сообщениям) ---
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    try:
        user_text = message.text or ""
        reply = generate_openai_reply(user_text)
        bot.send_message(message.chat.id, reply)
    except Exception as e:
        try:
            bot.send_message(message.chat.id, f"Ошибка: {e}")
        except:
            pass

# --- Flask маршруты ---
@app.route("/", methods=["GET"])
def index():
    return "OK", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    json_update = request.get_json(force=True)
    update = telebot.types.Update.de_json(json_update)
    bot.process_new_updates([update])
    return "", 200

# --- Устанавливаем webhook (если задан WEBHOOK_URL) ---
if WEBHOOK_URL:
    # удаляем старый webhook (если есть) и ставим новый
    try:
        bot.remove_webhook()
    except Exception:
        pass

    # Telegram требует полный https URL к endpoint'у
    set_ok = bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    print("set_webhook =>", set_ok)

# NOTE: старт приложения будет через gunicorn (на Render), поэтому тут ничего не делаем
