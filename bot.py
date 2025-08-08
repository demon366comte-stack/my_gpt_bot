import os
import telebot
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not OPENAI_API_KEY or not TELEGRAM_TOKEN:
    print("ERROR: отсутствует OPENAI_API_KEY или TELEGRAM_TOKEN в окружении.")
    raise SystemExit(1)

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты полезный и дружелюбный помощник."},
                {"role": "user", "content": message.text}
            ]
        )
        # возможна разница в структуре ответа — проверяем аккуратно:
        text = ""
        try:
            text = completion.choices[0].message.content
        except Exception:
            text = str(completion)
        bot.reply_to(message, text)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

if __name__ == "__main__":
    print("БОТ запущен!")
    bot.infinity_polling()

