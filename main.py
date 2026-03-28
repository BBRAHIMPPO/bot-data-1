import telebot
from instagrapi import Client
import json
import time
from threading import Thread

# --- إعدادات البوت ---
TOKEN = '7707660693:AAG98DsquCzScvjTkt-6ezSVHOCd9Wmz6nE'
bot = telebot.TeleBot(TOKEN)
cl = Client()

def start_reposting(chat_id):
    bot.send_message(chat_id, "🚀 بدأت عملية النشر التلقائي باستخدام الكوكيز...")
    keywords = ["fixed match", "correct score", "betting tips"]
    
    while True:
        try:
            import random
            word = random.choice(keywords)
            posts = cl.fbsearch_threads(word)
            
            for post in posts:
                caption = post.caption_text if post.caption_text else "Big Win! 💰"
                # إضافة لمستك الخاصة (رابط قناتك مثلاً)
                final_caption = f"{caption}\n\nJoin us for more: t.me/YourChannel"
                
                cl.thread_create(final_caption)
                bot.send_message(chat_id, "✅ تم نسخ ونشر منشور جديد بنجاح!")
                
                # استراحة لضمان الوصول لـ 300 منشور يومياً
                time.sleep(random.randint(250, 300))
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

@bot.message_handler(func=lambda m: m.text == "666")
def login_with_captured_cookies(message):
    try:
        # هذه هي القيم المأخوذة من الصورة التي أرفقتها
        custom_settings = {
            "cookie_jar": {
                "csrftoken": "qF4AIHtBSwGd8piuKvuB6KRJCYbb2Lx5",
                "ds_user_id": "69495189513",
                "mid": "aRHqtwALAAERcjl_CRhWDjQuqinD",
                "ig_did": "23D5D788-8746-454E-A42C-F6A7DA37E04C",
                "sessionid": "حط_هنا_قيمة_sessionid_من_المتصفح" 
            }
        }
        
        # تحميل الإعدادات في المتصفح الوهمي للبوت
        cl.set_settings(custom_settings)
        
        # اختبار الدخول
        bot.send_message(message.chat.id, "⏳ جاري التحقق من الكوكيز...")
        user_info = cl.user_info_by_username("joseph_fixeed") 
        bot.send_message(message.chat.id, f"✅ تم تسجيل الدخول بنجاح لحساب: {user_info.full_name}")
        
        # بدء النشر
        Thread(target=start_reposting, args=(message.chat.id,)).start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ فشل الدخول، تأكد من قيمة sessionid: {e}")

bot.polling()
