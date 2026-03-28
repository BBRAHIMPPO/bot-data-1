import telebot
import requests
from bs4 import BeautifulSoup
import re
import time
from flask import Flask
from threading import Thread
import os

# --- الإعدادات ---
TOKEN = '7707660693:AAG98DsquCzScvjTkt-6ezSVHOCd9Wmz6nE'
bot = telebot.TeleBot(TOKEN)
ADMIN_CODE = "666"

# ملفات حفظ البيانات
HISTORY_FILE = "found_links.txt"
ADMIN_FILE = "admin_users.txt" 

# --- نظام الفلترة الصارم لمنع التكرار نهائياً ---
seen_links = set()

# تحميل الروابط القديمة عند تشغيل البوت لكي لا يعيد إرسالها
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        for line in f:
            seen_links.add(line.strip().lower())

# سيرفر إبقاء البوت حياً على Render
app = Flask('')
@app.route('/')
def home(): return "BOT IS ACTIVE 24/7"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# --- دوال التحقق من الأدمن ---
def is_admin(chat_id):
    if not os.path.exists(ADMIN_FILE): return False
    with open(ADMIN_FILE, "r") as f:
        return str(chat_id) in f.read()

def add_admin(chat_id):
    if not is_admin(chat_id):
        with open(ADMIN_FILE, "a") as f:
            f.write(str(chat_id) + "\n")

# --- محرك البحث التلقائي 24/24 ---
def auto_scraper_loop(chat_id):
    bot.send_message(chat_id, "✅ تم تفعيل البحث 24/24. البوت الآن يراقب Threads ولن يرسل أي رابط مكرر نهائياً.")
    
    queries = [
        'site:threads.net "t.me/" "fixed matches"',
        'site:threads.net "t.me/" "correct score"',
        'site:threads.net "t.me/" "bet"'
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    while True:
        for query in queries:
            try:
                url = f"https://html.duckduckgo.com/html/?q={query}"
                res = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                text = soup.get_text()
                
                # استخراج معرف القناة فقط بدقة عالية
                links = re.findall(r't\.me/([a-zA-Z0-9_]+)', text)
                
                for l in links:
                    # تنظيف الرابط وتوحيد صيغته لمنع التكرار
                    clean_link = f"https://t.me/{l}".lower()
                    
                    if clean_link not in seen_links:
                        # إضافة الرابط للذاكرة والملف
                        seen_links.add(clean_link)
                        with open(HISTORY_FILE, "a") as f:
                            f.write(clean_link + "\n")
                            
                        bot.send_message(chat_id, f"🎯 **رابط جديد من Threads:**\n{clean_link}")
                        time.sleep(2)
            except Exception as e:
                pass 
            
            time.sleep(20)
        
        time.sleep(900)

# --- أوامر البوت ---
@bot.message_handler(commands=['start'])
def start(message):
    # إيقاف رسالة الترحيب نهائياً بمجرد أن تصبح أدمن
    if is_admin(message.chat.id):
        return 
    bot.reply_to(message, "أرسل كود التفعيل.")

@bot.message_handler(func=lambda m: m.text == ADMIN_CODE)
def handle_code(message):
    chat_id = message.chat.id
    if not is_admin(chat_id):
        add_admin(chat_id)
        Thread(target=auto_scraper_loop, args=(chat_id,)).start()
    else:
        bot.send_message(chat_id, "⚙️ نظام البحث التلقائي شغال بالفعل في الخلفية.")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("SCRAPER IS RUNNING 24/7...")
    bot.polling(none_stop=True)
