import time
import random
import os
import threading
from flask import Flask
import telebot

TOKEN = '8762517288:AAFPSd4rv5z5RZRv8xHABt4ALcC25fMpoBA'

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)

def get_odds(home, away):
    total = home + away
    if total == 0:
        return round(random.uniform(9.0, 11.0), 2)
    elif total <= 2:
        return round(random.uniform(12.0, 18.0), 2)
    elif total <= 4:
        return round(random.uniform(19.0, 30.0), 2)
    elif total <= 7:
        return round(random.uniform(31.0, 42.0), 2)
    else:
        return round(random.uniform(43.0, 50.0), 2)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_id = message.photo[-1].file_id

        for home in range(7):
            for away in range(7):
                score = f"{home} - {away}"
                odds = get_odds(home, away)

                caption = (
                    f"<b>100 % Real Information</b>\n\n"
                    f"<b>Tip : Correct Score ( {score} ) FT</b>\n\n"
                    f"<b>Odd : {odds}</b>\n\n"
                    f"<b>This Match Is 100% Safe And it's Trusted And Guaranteed</b>\n\n"
                    f"<b>Available on all betting sites 🤝</b>"
                )

                bot.send_photo(message.chat.id, file_id, caption=caption, parse_mode='HTML')
                time.sleep(0.3)

    except Exception as e:
        print(f"Error: {e}")

def start_polling():
    while True:
        try:
            print("Clearing webhook...")
            bot.remove_webhook()
            time.sleep(2)
            print("Bot started polling...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Polling error: {e}. Retrying in 15s...")
            time.sleep(15)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    start_polling()
