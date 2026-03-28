import telebot
from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired, ChallengeRequired
from threading import Thread
import time
import random
from flask import Flask

# --- الإعدادات ---
TOKEN = '8678424700:AAFSt9OSJCvz9kFGJBxskW74a-euN4Oe994'
bot = telebot.TeleBot(TOKEN)
cl = Client()
app = Flask('')

@app.route('/')
def home(): return "JOSEPH_FIXED_ACTIVE"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

user_creds = {}

def start_reposting(chat_id):
    bot.send_message(chat_id, "🚀 تم الدخول بنجاح! جاري البدء...")
    keywords = ["fixed match", "correct score", "betting"]
    while True:
        try:
            word = random.choice(keywords)
            posts = cl.fbsearch_threads(word)
            for post in posts:
                caption = post.caption_text if post.caption_text else "Big Win! 💰"
                cl.thread_create(caption)
                bot.send_message(chat_id, f"✅ تم نشر منشور جديد!")
                time.sleep(random.randint(250, 320))
                break
        except Exception as e:
            time.sleep(60)

@bot.message_handler(func=lambda m: m.text == "666")
def ask_username(message):
    bot.send_message(message.chat.id, "👤 أرسل اسم المستخدم (Username):")
    bot.register_next_step_handler(message, get_password)

def get_password(message):
    user_creds[message.chat.id] = {'username': message.text}
    bot.send_message(message.chat.id, "🔑 أرسل كلمة السر (Password):")
    bot.register_next_step_handler(message, attempt_login)

def attempt_login(message):
    chat_id = message.chat.id
    password = message.text
    username = user_creds[chat_id]['username']
    bot.send_message(chat_id, "⏳ جاري محاولة تسجيل الدخول...")
    try:
        cl.login(username, password)
        start_reposting(chat_id)
    except TwoFactorRequired:
        bot.send_message(chat_id, "🔐 أرسل رمز التأكيد (OTP):")
        bot.register_next_step_handler(message, verify_otp)
    except Exception as e:
        bot.send_message(chat_id, f"❌ خطأ: {e}")

def verify_otp(message):
    try:
        cl.two_factor_login(message.text)
        start_reposting(message.chat.id)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ الرمز خطأ: {e}")

if __name__ == "__main__":
    # تشغيل Flask في خيط منفصل لإبقاء Render حياً
    Thread(target=run_flask).start()
    
    # --- الحل السحري لمشكلة Conflict 409 ---
    bot.remove_webhook() # مسح أي ارتباط قديم
    time.sleep(1)        # انتظار ثانية للتأكد
    
    print("Bot is starting...")
    # استخدام non_stop=True لضمان عدم توقف البوت عند حدوث خطأ بسيط
    bot.polling(none_stop=True, interval=0, timeout=20)
