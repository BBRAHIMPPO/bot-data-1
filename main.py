import telebot
from instagrapi import Client
from flask import Flask
from threading import Thread
import time
import random
import os

# --- الإعدادات ---
TOKEN = '7707660693:AAG98DsquCzScvjTkt-6ezSVHOCd9Wmz6nE'
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = "666" # كود التفعيل

# حسابك في Threads
USERNAME = 'YOUR_USERNAME'
PASSWORD = 'YOUR_PASSWORD'

cl = Client()
app = Flask('')

@app.route('/')
def home(): return "AUTO_POSTER_ACTIVE"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# قاعدة بيانات للمنشورات المسروقة لمنع التكرار
posted_ids = set()

def auto_reposter(chat_id):
    bot.send_message(chat_id, "🚀 نظام النسخ واللصق التلقائي بدأ (الهدف: 300 منشور/يوم).")
    
    # تسجيل الدخول
    try:
        cl.login(USERNAME, PASSWORD)
    except Exception as e:
        bot.send_message(chat_id, f"❌ خطأ في الدخول للحساب: {e}")
        return

    keywords = ["fixed match", "correct score", "betting tips", "HT/FT"]
    
    while True:
        try:
            # 1. البحث عن منشورات جديدة لسرقتها
            target_word = random.choice(keywords)
            posts = cl.fbsearch_threads(target_word)
            
            for post in posts:
                if post.id not in posted_ids:
                    # 2. تحميل الصورة إذا كانت موجودة
                    image_path = None
                    if post.image_versions2:
                        image_path = cl.photo_download(post.pk, folder="/tmp")
                    
                    # 3. إعادة النشر في حسابك (Copy/Paste)
                    caption = post.caption_text if post.caption_text else "Big Win! 💰"
                    
                    if image_path:
                        cl.thread_create(caption, image_url=image_path)
                    else:
                        cl.thread_create(caption)
                    
                    # 4. تسجيل العملية وإعلامك في تيليجرام
                    posted_ids.add(post.id)
                    bot.send_message(chat_id, f"✅ تم نشر منشور جديد بنجاح!\n📝 النص: {caption[:50]}...")
                    
                    # استراحة عشوائية لتبدو كإنسان (بين 3 و 6 دقائق)
                    # 300 منشور في 24 ساعة تعني منشور كل 4.8 دقائق تقريباً
                    wait_time = random.randint(180, 360) 
                    time.sleep(wait_time)
                    
        except Exception as e:
            print(f"Error during reposting: {e}")
            time.sleep(60)

@bot.message_handler(func=lambda m: m.text == ADMIN_ID)
def start_bot(message):
    Thread(target=auto_reposter, args=(message.chat.id,)).start()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
