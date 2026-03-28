import telebot
import requests
from bs4 import BeautifulSoup
import re
import time
import random
from flask import Flask
from threading import Thread
import os

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
def home(): return "JOSEPH_FIXED_ACTIVE"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def is_admin(chat_id):
    if not os.path.exists(ADMIN_FILE): return False
    with open(ADMIN_FILE, "r") as f:
        return str(chat_id) in f.read()

def add_admin(chat_id):
    if not is_admin(chat_id):
        with open(ADMIN_FILE, "a") as f:
            f.write(str(chat_id) + "\n")

def auto_scraper_loop(chat_id):
    bot.send_message(chat_id, "🚀 نظام السحب الشرس بدأ الآن. سأفحص كل الزوايا في Threads.")
    
    # كلمات دلالية أوسع لضمان إيجاد نتائج
    queries = [
        'site:threads.net "t.me/"',
        'site:threads.net "telegram link"',
        'site:threads.net "join my channel"',
        'site:threads.net "fixed" "t.me"',
        'site:threads.net "betting" "t.me"'
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    while True:
        found_in_round = 0
        for query in queries:
            try:
                # إضافة رقم عشوائي للبحث لتجديد النتائج
                search_url = f"https://html.duckduckgo.com/html/?q={query}&t=h_&df=d" # df=d تبحث عن نتائج اليوم فقط
                res = requests.get(search_url, headers=headers, timeout=15)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                links = re.findall(r't\.me/([a-zA-Z0-9_]{5,})', soup.get_text())
                
                for l in links:
                    clean_link = f"https://t.me/{l}".lower()
                    if clean_link not in seen_links:
                        seen_links.add(clean_link)
                        with open(HISTORY_FILE, "a") as f:
                            f.write(clean_link + "\n")
                        bot.send_message(chat_id, f"🎯 **رابط جديد مكتشف:**\n{clean_link}")
                        found_in_round += 1
                
                time.sleep(10) # انتظار بين كل Query
            except Exception as e:
                print(f"Error: {e}")
        
        # إذا لم يجد شيئاً، يرسل إشارة بسيطة (يمكنك حذف هذا السطر إذا لم ترده)
        if found_in_round == 0:
            print("No new links this round. Sleeping...")

        time.sleep(600) # فحص كل 10 دقائق

@bot.message_handler(commands=['start'])
def start(message):
    if is_admin(message.chat.id): return 
    bot.reply_to(message, "أرسل كود التفعيل.")

@bot.message_handler(func=lambda m: m.text == ADMIN_CODE)
def handle_code(message):
    chat_id = message.chat.id
    if not is_admin(chat_id):
        add_admin(chat_id)
        Thread(target=auto_scraper_loop, args=(chat_id,)).start()
    else:
        bot.send_message(chat_id, "⚙️ النظام شغال بالفعل ويراقب Threads.")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
