import telebot
from instagrapi import Client
import json
import time
import random
from threading import Thread
from flask import Flask

# --- الإعدادات الجديدة ---
TOKEN = '8678424700:AAFSt9OSJCvz9kFGJBxskW74a-euN4Oe994'
bot = telebot.TeleBot(TOKEN)
cl = Client()
app = Flask('')

@app.route('/')
def home(): return "JOSEPH_FIXED_BOT_ACTIVE"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# --- نظام النسخ والنشر التلقائي ---
def start_reposting(chat_id):
    bot.send_message(chat_id, "🚀 تم تفعيل نظام النسخ واللصق الذكي. سأقوم بنشر حوالي 300 منشور يومياً.")
    keywords = ["fixed match", "correct score", "betting tips", "HT/FT"]
    
    while True:
        try:
            word = random.choice(keywords)
            posts = cl.fbsearch_threads(word)
            
            for post in posts:
                # سحب النص والصورة
                caption = post.caption_text if post.caption_text else "Big Win! 💰"
                image_path = None
                if post.image_versions2:
                    try:
                        image_path = cl.photo_download(post.pk, folder="/tmp")
                    except: pass

                # النشر في حسابك
                if image_path:
                    cl.thread_create(caption, image_url=image_path)
                else:
                    cl.thread_create(caption)
                
                bot.send_message(chat_id, f"✅ تم نشر منشور جديد بنجاح!")
                
                # استراحة بين 4 و 5 دقائق للوصول لمعدل 300 يومياً
                time.sleep(random.randint(250, 300))
                break 
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

# --- تسجيل الدخول باستخدام الكوكيز من الصورة ---
@bot.message_handler(func=lambda m: m.text == "666")
def login_with_cookies(message):
    bot.send_message(message.chat.id, "⏳ جاري الدخول باستخدام الكوكيز المستخرجة...")
    
    try:
        # القيم مأخوذة مباشرة من الصورة التي أرفقتها
        cl.set_settings({
            "cookie_jar": {
                "csrftoken": "qF4AIHtBSwGd8piuKvuB6KRJCYbb2Lx5",
                "ds_user_id": "69495189513",
                "ig_did": "23D5D788-8746-454E-A42C-F6A7DA37E04C",
                "mid": "aRHqtwALAAERcjl_CRhWDjQuqinD",
                "sessionid": "ضعه_هنا" # اسحب الشريط في المتصفح للأسفل وانسخ قيمة sessionid
            }
        })
        
        # التحقق من نجاح الدخول
        user_info = cl.user_info_by_username("joseph_fixeed")
        bot.send_message(message.chat.id, f"✅ تم تسجيل الدخول بنجاح لحساب: {user_info.full_name}")
        
        # بدء العمل
        Thread(target=start_reposting, args=(message.chat.id,)).start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ فشل الدخول. تأكد من قيمة sessionid الصحيحة: {e}")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.polling(none_stop=True)
