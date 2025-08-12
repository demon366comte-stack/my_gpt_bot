import os
import telebot
import threading
from flask import Flask

# Загружаем токены из переменных окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Создаём Flask-приложение
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

# Здесь твоя логика бота
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Привет! Я бот и я работаю на Render!")

# Функция для запуска бота
def run_bot():
    bot.polling(none_stop=True)

# Функция для запуска Flask
def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    threading.Thread(target=run_bot).start()
    # Запускаем Flask-сервер
    run_flask()

