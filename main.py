import telebot
import sqlite3
import time
import os
from flask import Flask
from threading import Thread

# البيانات الخاصة بك
TOKEN = "7225070696:AAEBSquEmyDCzz0o65GoVPHIG2Xk5qBf_Lg"
SECRET_CODE = "7779900009"
ADMIN_ID = 5077384676  # الآيدي ديالك لي فالتصويرة

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def index(): return "Bot Status: Online"

# قاعدة البيانات
conn = sqlite3.connect('bot_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, username TEXT)')
conn.commit()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username or "لا يوجد"
    
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (user_id, name, username))
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        
        # الإشعار اللي بغيتي (نفس شكل الصورة)
        msg = f"👾 تم دخول شخص جديد إلى البوت الخاص بك 👾\n"
        msg += f"------------------------------\n"
        msg += f"• معلومات العضو الجديد .\n\n"
        msg += f"• الاسم : {name}\n"
        msg += f"• معرف : @{username}\n"
        msg += f"• الايدي : {user_id}\n"
        msg += f"------------------------------\n"
        msg += f"• عدد الأعضاء الكلي : {total}"
        try: bot.send_message(ADMIN_ID, msg)
        except: pass
    bot.reply_to(message, "مرحباً بك!")

@bot.message_handler(func=lambda m: m.text == SECRET_CODE)
def send_all(message):
    if message.reply_to_message:
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        bot.reply_to(message, f"🚀 جاري الإرسال لـ {len(users)} عضو...")
        for u in users:
            try:
                bot.forward_message(u[0], message.chat.id, message.reply_to_message.id)
                time.sleep(0.05)
            except: pass
        bot.send_message(message.chat.id, "✅ تم الإرسال للجميع!")

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
