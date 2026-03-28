import telebot
from instagrapi import Client
import re
import time
from flask import Flask
from threading import Thread

# --- إعدادات السيرفر الوهمي للبقاء حياً ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعدادات البوت ---
TOKEN = '7707660693:AAG98DsquCzScvjTkt-6ezSVHOCd9Wmz6nE'
bot = telebot.TeleBot(TOKEN)
SECRET_CODE = "666"
user_data = {}
cl = Client()

def scrape_threads_links(chat_id):
    bot.send_message(chat_id, "🔍 جاري الفحص... يرجى الانتظار.")
    try:
        cl.login(user_data[chat_id]['username'], user_data[chat_id]['password'])
        keywords = ["fixed matches", "correct score", "t.me/"]
        found_links = set()
        for word in keywords:
            posts = cl.fbsearch_threads(word)
            for post in posts:
                text = post.caption_text if post.caption_text else ""
                links = re.findall(r't\.me/[\w\d_]+', text)
                for l in links:
                    full_link = f"https://{l}"
                    if full_link not in found_links:
                        bot.send_message(chat_id, f"✅ قناة جديدة:\n{full_link}")
                        found_links.add(full_link)
        if not found_links:
            bot.send_message(chat_id, "📭 لا توجد روابط جديدة.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ خطأ: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "أرسل الكود للتفعيل.")

@bot.message_handler(func=lambda m: m.text == SECRET_CODE)
def ask_username(message):
    user_data[message.chat.id] = {'step': 'get_user'}
    bot.send_message(message.chat.id, "🔐 أرسل Username الخاص بـ Threads:")

@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('step') == 'get_user')
def get_username(message):
    user_data[message.chat.id]['username'] = message.text
    user_data[message.chat.id]['step'] = 'get_pass'
    bot.send_message(message.chat.id, "📥 أرسل Password:")

@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('step') == 'get_pass')
def get_password(message):
    user_data[message.chat.id]['password'] = message.text
    user_data[message.chat.id]['step'] = 'active'
    bot.send_message(message.chat.id, "✅ جاري بدء الفحص...")
    scrape_threads_links(message.chat.id)

if __name__ == "__main__":
    keep_alive() # تشغيل السيرفر الوهمي
    print("Bot is alive!")
    bot.polling(none_stop=True)
