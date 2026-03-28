import telebot
import requests
import re
import time
from flask import Flask
from threading import Thread
import os

# --- الإعدادات ---
TOKEN = '7707660693:AAG98DsquCzScvjTkt-6ezSVHOCd9Wmz6nE'
bot = telebot.TeleBot(TOKEN)
ADMIN_CODE = "666"

HISTORY_FILE = "found_links.txt"
ADMIN_FILE = "admin_users.txt" 
seen_links = set()

if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        for line in f:
            seen_links.add(line.strip().lower())

app = Flask('')
@app.route('/')
def home(): return "HIGH_SPEED_SCRAPER_ACTIVE"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def is_admin(chat_id):
    if not os.path.exists(ADMIN_FILE): return False
    with open(ADMIN_FILE, "r") as f:
        return str(chat_id) in f.read()

def add_admin(chat_id):
    if not is_admin(chat_id):
        with open(ADMIN_FILE, "a") as f: f.write(str(chat_id) + "\n")

# --- محرك السحب السريع (السرعة القصوى) ---
def ultra_fast_scraper(chat_id):
    bot.send_message(chat_id, "🔥 تم تفعيل السحب السريع. سأقوم الآن بفحص Threads مباشرة وبأعلى تردد ممكن.")
    
    # روابط استكشاف Threads المباشرة (التي لا تتطلب تسجيل دخول)
    targets = [
        "https://www.threads.net/search?q=t.me&serp_type=tags",
        "https://www.threads.net/search?q=fixed%20matches",
        "https://www.threads.net/search?q=correct%20score"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.threads.net/"
    }

    while True:
        for url in targets:
            try:
                # محاولة جلب الصفحة مباشرة
                response = requests.get(url, headers=headers, timeout=10)
                # استخراج الروابط باستخدام Regex من الكود المصدري (JSON/HTML)
                raw_links = re.findall(r't\.me\/([a-zA-Z0-9_]{5,})', response.text)
                
                for l in raw_links:
                    clean_link = f"https://t.me/{l}".lower()
                    if clean_link not in seen_links:
                        seen_links.add(clean_link)
                        with open(HISTORY_FILE, "a") as f:
                            f.write(clean_link + "\n")
                        
                        bot.send_message(chat_id, f"🎯 **رابط جديد:** {clean_link}")
                        time.sleep(0.5) # سرعة عالية جداً في الإرسال
                
            except Exception as e:
                print(f"Error: {e}")
            
            # استراحة قصيرة جداً (ثانية واحدة) بين الأهداف لضمان السرعة
            time.sleep(1)
        
        # إعادة الدورة فوراً للحصول على أحدث المنشورات
        time.sleep(5)

@bot.message_handler(commands=['start'])
def start(message):
    if is_admin(message.chat.id): return 
    bot.reply_to(message, "أرسل كود التفعيل.")

@bot.message_handler(func=lambda m: m.text == ADMIN_CODE)
def handle_code(message):
    chat_id = message.chat.id
    if not is_admin(chat_id):
        add_admin(chat_id)
        Thread(target=ultra_fast_scraper, args=(chat_id,)).start()
    else:
        bot.send_message(chat_id, "⚙️ نظام السرعة القصوى يعمل بالفعل.")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
