import telebot
import sqlite3
import time
import os

# التوكن الخاص بك
TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
SECRET_CODE = "7779900009"
ADMIN_ID = 5077384676 # جرب تحط الايدي ديالك هنا باش يوصلوك الإشعارات

bot = telebot.TeleBot(TOKEN)

# إعداد قاعدة البيانات (SQLite)
# ملاحظة: فـ Render، البيانات غتمسح إلى طفا البوت إلا إلى استعملتي Database خارجية بحال PostgreSQL
# هاد الكود غيخدم، ولكن حاول ما تطفيهش بزاف
db_path = 'bot_data.db'
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT)')
conn.commit()

def get_total_users():
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username or "لا يوجد"

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, name, username) VALUES (?, ?, ?)", (user_id, first_name, username))
        conn.commit()
        
        total = get_total_users()
        admin_msg = f"👾 تم دخول شخص جديد 👾\n----------\n• الاسم : {first_name}\n• الايدي : {user_id}\n----------\n• الكلي : {total}"
        try:
            bot.send_message(ADMIN_ID, admin_msg)
        except:
            pass
    bot.reply_to(message, "مرحباً بك!")

@bot.message_handler(func=lambda message: message.text == SECRET_CODE)
def broadcast(message):
    if message.reply_to_message:
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        bot.reply_to(message, f"🚀 جاري الإرسال لـ {len(users)} عضو...")
        
        for user in users:
            try:
                bot.forward_message(user[0], message.chat.id, message.reply_to_message.message_id)
                time.sleep(0.05) 
            except:
                pass
        bot.send_message(message.chat.id, "✅ انتهى الإرسال!")

# هاد الجزء ضروري لـ Render باش كيعرف البوت راه خدام
from flask import Flask
app = Flask(__name__)
@app.route('/')
def index(): return "Bot is Running!"

if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))).start()
    print("Bot is alive...")
    bot.infinity_polling()
