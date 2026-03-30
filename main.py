import threading
import time
import random
import os
from flask import Flask # غادي نزيدو هادي باش Render يرتاح
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import telebot

# --- إعداد Flask لـ Render ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- إعدادات البوت ---
TOKEN = "8678424700:AAFSt9OSJCvz9kFGJBxskW74a-euN4Oe994"
bot = telebot.TeleBot(TOKEN)
is_running = False
seen_links = set()

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_bin = os.environ.get("GOOGLE_CHROME_BIN")
    if chrome_bin: chrome_options.binary_location = chrome_bin
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def scrape_logic(chat_id):
    global is_running
    driver = None
    while is_running:
        try:
            if not driver: driver = get_driver()
            # ... (نفس منطق السكرابينغ اللي عطيتهولك قبل) ...
            driver.get("https://www.threads.net/search?q=correct%20score")
            time.sleep(10)
            bot.send_message(chat_id, "🔍 البحث شغال...")
            time.sleep(300)
        except Exception as e:
            if driver: driver.quit()
            driver = None
            time.sleep(20)

@bot.message_handler(func=lambda m: m.text == "999")
def start(m):
    global is_running
    if not is_running:
        is_running = True
        bot.reply_to(m, "🚀 انطلقنا!")
        threading.Thread(target=scrape_logic, args=(m.chat.id,)).start()

# تشغيل Flask في الخلفية
threading.Thread(target=run_flask).start()

# تشغيل البوت
print("🤖 Bot is active...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)
