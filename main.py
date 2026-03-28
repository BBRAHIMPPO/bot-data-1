import telebot
from instagrapi import Client
from flask import Flask
from threading import Thread
import re
import os
import time

# --- الإعدادات الأساسية ---
TOKEN = '7707660693:AAG98DsquCzScvjTkt-6ezSVHOCd9Wmz6nE'
bot = telebot.TeleBot(TOKEN)
cl = Client()
SESSION_PATH = "threads_session.json"
HISTORY_FILE = "links_history.txt"

# سيرفر إبقاء البوت حياً على Render
app = Flask('')
@app.route('/')
def home(): return "JOSEPH_FIXED_BOT_ACTIVE"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# قاموس لتتبع حالة كل مستخدم
user_states = {}

# --- دوال مساعدة ---
def save_link(link):
    with open(HISTORY_FILE, "a") as f:
        f.write(link + "\n")

def is_old_link(link):
    if not os.path.exists(HISTORY_FILE): return False
    with open(HISTORY_FILE, "r") as f:
        return link in f.read()

# --- دالة البحث المتقدمة ---
def deep_scrape(chat_id):
    bot.send_message(chat_id, "🚀 بدأنا الفحص الشامل لـ Threads... سأرسل لك كل قناة جديدة أجدها.")
    # كلمات البحث المستهدفة
    keywords = ["fixed matches", "correct score", "betting tips", "t.me/", "HT/FT"]
    
    while True: # دورة بحث مستمرة
        try:
            for word in keywords:
                posts = cl.fbsearch_threads(word)
                for post in posts:
                    text = post.caption_text if post.caption_text else ""
                    links = re.findall(r't\.me/[\w\d_]+', text)
                    for l in links:
                        full_link = f"https://{l}"
                        if not is_old_link(full_link):
                            bot.send_message(chat_id, f"🎯 **قناة جديدة مكتشفة:**\n\n{full_link}\n\n🔗 المصدر: threads.net/t/{post.code}")
                            save_link(full_link)
                            time.sleep(2)
            time.sleep(600) # انتظر 10 دقائق قبل الفحص التالي لتجنب الحظر
        except Exception as e:
            print(f"Scrape Error: {e}")
            time.sleep(60)

# --- معالجة الرسائل والسيناريوهات ---

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "مرحباً! أرسل كود التفعيل (666) لربط حسابك والبدء.")

@bot.message_handler(func=lambda m: m.text == "666")
def init_login(message):
    user_states[message.chat.id] = {'step': 'username'}
    bot.send_message(message.chat.id, "👤 أرسل اسم المستخدم (Username) لـ Threads:")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'username')
def get_user(message):
    user_states[message.chat.id]['user'] = message.text
    user_states[message.chat.id]['step'] = 'pass'
    bot.send_message(message.chat.id, "🔑 أرسل كلمة المرور (Password):")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'pass')
def finalize_login(message):
    chat_id = message.chat.id
    username = user_states[chat_id]['user']
    password = message.text
    
    bot.send_message(chat_id, "⏳ جاري محاولة تسجيل الدخول... قد يطلب منك كود التحقق.")
    
    try:
        # محاولة تحميل جلسة سابقة لتجنب الـ Challenge
        if os.path.exists(SESSION_PATH):
            cl.load_settings(SESSION_PATH)
        
        cl.login(username, password)
        cl.dump_settings(SESSION_PATH)
        
        bot.send_message(chat_id, "✅ تسجيل دخول ناجح! سأبدأ العمل الآن.")
        Thread(target=deep_scrape, args=(chat_id,)).start()
        
    except Exception as e:
        error_msg = str(e)
        if "challenge_required" in error_msg:
            user_states[chat_id]['step'] = 'otp'
            bot.send_message(chat_id, "⚠️ Meta تطلب كود التحقق. أرسل الكود المكون من 6 أرقام هنا:")
        else:
            bot.send_message(chat_id, f"❌ خطأ غير متوقع: {error_msg}")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'otp')
def handle_otp(message):
    chat_id = message.chat.id
    otp_code = message.text
    try:
        # استكمال الدخول باستخدام الكود
        cl.login(user_states[chat_id]['user'], user_states[chat_id]['pass'], verification_code=otp_code)
        cl.dump_settings(SESSION_PATH)
        bot.send_message(chat_id, "✅ تم فك التشفير بنجاح! جاري البدء...")
        Thread(target=deep_scrape, args=(chat_id,)).start()
    except Exception as e:
        bot.send_message(chat_id, f"❌ الكود خاطئ أو انتهت صلاحيته: {e}")

# --- تشغيل البوت ---
if __name__ == "__main__":
    Thread(target=run_flask).start() # تشغيل Flask لإبقاء Render مستيقظاً
    print("JOSEPH_FIXED BOT IS RUNNING...")
    bot.polling(none_stop=True)
