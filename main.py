import telebot
from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired, ChallengeRequired
from threading import Thread
import time
import random

# --- الإعدادات ---
TOKEN = '8678424700:AAFSt9OSJCvz9kFGJBxskW74a-euN4Oe994'
bot = telebot.TeleBot(TOKEN)
cl = Client()

user_creds = {}

def start_reposting(chat_id):
    bot.send_message(chat_id, "🚀 تم الدخول بنجاح! جاري بدء نظام النسخ التلقائي (300 منشور يومياً).")
    # كلمات البحث عن "القمر" أو "المراهنات" حسب اهتمامك
    keywords = ["fixed match", "correct score", "betting"]
    while True:
        try:
            word = random.choice(keywords)
            posts = cl.fbsearch_threads(word)
            for post in posts:
                caption = post.caption_text if post.caption_text else "Big Win! 💰"
                cl.thread_create(caption)
                bot.send_message(chat_id, f"✅ تم نشر منشور جديد بنجاح من Threads!")
                time.sleep(random.randint(250, 320)) # توقيت عشوائي للوصول لـ 300 منشور
                break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

# --- مراحل تسجيل الدخول ---
@bot.message_handler(func=lambda m: m.text == "666")
def ask_username(message):
    bot.send_message(message.chat.id, "👤 أرسل اسم المستخدم (Username) الخاص بـ Threads:")
    bot.register_next_step_handler(message, get_password)

def get_password(message):
    user_creds[message.chat.id] = {'username': message.text}
    bot.send_message(message.chat.id, "🔑 أرسل كلمة السر (Password):")
    bot.register_next_step_handler(message, attempt_login)

def attempt_login(message):
    chat_id = message.chat.id
    password = message.text
    username = user_creds[chat_id]['username']
    
    bot.send_message(chat_id, "⏳ جاري محاولة تسجيل الدخول... يرجى الانتظار.")
    
    try:
        cl.login(username, password)
        # إذا مر تسجيل الدخول بنجاح
        start_reposting(chat_id)
        
    except TwoFactorRequired:
        bot.send_message(chat_id, "🔐 الحساب محمي بـ (2FA). يرجى إرسال رمز التأكيد الذي وصلك:")
        bot.register_next_step_handler(message, verify_otp)
        
    except ChallengeRequired:
        bot.send_message(chat_id, "⚠️ طلب إنستغرام تأكيد الهوية (Challenge). افتح التطبيق واضغط 'It was me' ثم حاول مجدداً.")
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ خطأ أثناء الدخول: {e}")

def verify_otp(message):
    otp_code = message.text
    chat_id = message.chat.id
    try:
        # إرسال رمز الـ OTP للنظام لإكمال الدخول
        cl.two_factor_login(otp_code)
        start_reposting(chat_id)
    except Exception as e:
        bot.send_message(chat_id, f"❌ الرمز غير صحيح أو حدث خطأ: {e}")

bot.polling(none_stop=True)
