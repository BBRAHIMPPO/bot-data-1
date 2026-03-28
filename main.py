import telebot
import requests
from bs4 import BeautifulSoup
import re
import time
from flask import Flask
from threading import Thread

# --- الإعدادات ---
TOKEN = '7707660693:AAG98DsquCzScvjTkt-6ezSVHOCd9Wmz6nE'
bot = telebot.TeleBot(TOKEN)
SECRET_CODE = "666"
HISTORY_FILE = "found_links.txt"

# سيرفر إبقاء البوت حياً على Render
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# --- دالة فحص الروابط المكررة ---
def is_duplicate(link):
    try:
        with open(HISTORY_FILE, "r") as f:
            return link in f.read()
    except FileNotFoundError:
        return False

def save_link(link):
    with open(HISTORY_FILE, "a") as f:
        f.write(link + "\n")

# --- دالة البحث بدون حساب (Scraper) ---
def fetch_links_without_login(chat_id):
    bot.send_message(chat_id, "🔍 جاري البحث في Threads عن روابط جديدة (بدون حساب)...")
    
    # كلمات البحث المستهدفة في Threads عبر Google
    search_queries = [
        'site:threads.net "t.me/" "fixed"',
        'site:threads.net "t.me/" "match"',
        'site:threads.net "t.me/" "correct score"'
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    found_count = 0
    for query in search_queries:
        try:
            # استخدام Google Search لسحب الروابط المؤرشفة من Threads
            url = f"https://www.google.com/search?q={query}"
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # البحث عن أي نص يشبه روابط تيليجرام في نتائج البحث
            all_text = soup.get_text()
            links = re.findall(r't\.me/[\w\d_]+', all_text)
            
            for l in links:
                full_link = f"https://{l}"
                if not is_duplicate(full_link):
                    bot.send_message(chat_id, f"🎯 تم العثور على قناة:\n{full_link}")
                    save_link(full_link)
                    found_count += 1
                    time.sleep(1)
                    
        except Exception as e:
            print(f"Error: {e}")

    if found_count == 0:
        bot.send_message(chat_id, "📭 لم أجد روابط جديدة حالياً. سأعيد المحاولة لاحقاً.")

# --- معالجة الأوامر ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "أهلاً بك في بوت سحب الروابط. أرسل 666 للبدء.")

@bot.message_handler(func=lambda m: m.text == SECRET_CODE)
def trigger_search(message):
    fetch_links_without_login(message.chat.id)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("Bot is running without login...")
    bot.polling(none_stop=True)
