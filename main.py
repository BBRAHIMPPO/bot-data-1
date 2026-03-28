import telebot
from instagrapi import Client
from threading import Thread
import time
import random

# --- الإعدادات ---
TOKEN = '8678424700:AAFSt9OSJCvz9kFGJBxskW74a-euN4Oe994'
bot = telebot.TeleBot(TOKEN)
cl = Client()

# مخزن مؤقت لحفظ القيم أثناء إدخالها
user_cookies = {}

# --- وظيفة النشر التلقائي ---
def start_reposting(chat_id):
    bot.send_message(chat_id, "🚀 تم الدخول! بدأت الآن عملية النسخ والنشر (الهدف 300 منشور).")
    keywords = ["fixed match", "correct score", "betting tips"]
    while True:
        try:
            word = random.choice(keywords)
            posts = cl.fbsearch_threads(word)
            for post in posts:
                caption = post.caption_text if post.caption_text else "Big Win! 💰"
                cl.thread_create(caption)
                bot.send_message(chat_id, "✅ تم نشر منشور جديد بنجاح!")
                time.sleep(random.randint(250, 320))
                break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

# --- نظام إدخال الكوكيز خطوة بخطوة ---
@bot.message_handler(func=lambda m: m.text == "666")
def start_cookie_steps(message):
    user_cookies[message.chat.id] = {}
    bot.send_message(message.chat.id, "1️⃣ أرسل قيمة **csrftoken**:")
    bot.register_next_step_handler(message, get_ds_user_id)

def get_ds_user_id(message):
    user_cookies[message.chat.id]['csrftoken'] = message.text
    bot.send_message(message.chat.id, "2️⃣ أرسل قيمة **ds_user_id**:")
    bot.register_next_step_handler(message, get_mid)

def get_mid(message):
    user_cookies[message.chat.id]['ds_user_id'] = message.text
    bot.send_message(message.chat.id, "3️⃣ أرسل قيمة **mid**:")
    bot.register_next_step_handler(message, get_ig_did)

def get_ig_did(message):
    user_cookies[message.chat.id]['mid'] = message.text
    bot.send_message(message.chat.id, "4️⃣ أرسل قيمة **ig_did**:")
    bot.register_next_step_handler(message, get_sessionid)

def get_sessionid(message):
    user_cookies[message.chat.id]['ig_did'] = message.text
    bot.send_message(message.chat.id, "5️⃣ أرسل القيمة الأهم **sessionid**:")
    bot.register_next_step_handler(message, final_login)

def final_login(message):
    user_cookies[message.chat.id]['sessionid'] = message.text
    bot.send_message(message.chat.id, "⏳ جاري محاولة الدخول بالقيم التي أدخلتها...")
    
    try:
        cookies = user_cookies[message.chat.id]
        cl.set_settings({"cookie_jar": cookies})
        
        # اختبار الجلسة
        cl.get_timeline_feed() 
        bot.send_message(message.chat.id, "✅ تم تسجيل الدخول بنجاح!")
        
        # بدء النشر التلقائي
        Thread(target=start_reposting, args=(message.chat.id,)).start()
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ فشل الدخول: {e}\nتأكد من أن sessionid لم تنتهِ صلاحيتها.")

bot.polling(none_stop=True)
