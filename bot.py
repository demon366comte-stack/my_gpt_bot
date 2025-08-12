import os
import telebot
from flask import Flask, request

TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)
APP_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"  # URL твоего приложения на Render

app = Flask(__name__)

# Обрабатываем команду /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой бот.")

# Flask маршрут для приёма данных от Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Устанавливаем webhook при старте
@app.before_first_request
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
