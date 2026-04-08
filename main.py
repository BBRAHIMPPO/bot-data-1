import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading
import os

# --- الإعدادات (تأكد من ملء هذه البيانات) ---
TOKEN = "8744376397:AAFsFf-AsevpB-L5btSksOIUljvcai1HUCw"
ADMIN_ID = 000000000  # 👈 حط الـ ID ديالك هنا ضروري باش يخدم ليك الكود السري
CHANNEL_ID = "-1002264628286" 
CHANNEL_LINK = "https://t.me/+lIwJqGViEdg1YmU0"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ملف حفظ المستخدمين
users_file = "database.txt"
if not os.path.exists(users_file):
    with open(users_file, "w") as f: pass

# حالة القفل (OFF للمراجعة، ON بعد القبول)
force_join_active = False 

# --- نظام Flask لتجاوز مشاكل Render ---
@app.route('/')
def health_check():
    return "Bot is running perfectly!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- وظائف التحقق ---
def is_member(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def get_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    options = [
        "Live Scores ⚽️", "Predictions 📈", "Match Stats 📊", "H2H Results ⚔️",
        "Lineups 🏟", "League Tables 📅", "Transfer News 📰", "Top Scorers 🏆",
        "Injury Updates 🚑", "Referee Stats 🏁", "Corner Stats 🚩", "Card Stats 🟨",
        "Odds Analysis 🎰", "Stadium Info 📍", "TV Channels 📺", "Daily Tips 💡",
        "Player Ratings ⭐", "Value Bets 💰", "VIP Insights 💎", "Support 🛠"
    ]
    buttons = [InlineKeyboardButton(opt, callback_data="info") for opt in options]
    markup.add(*buttons)
    return markup

# --- معالجة الرسائل ---

@bot.message_handler(commands=['start'])
def welcome(m):
    # تسجيل المستخدم وتنبيهك
    with open(users_file, "r+") as f:
        users = f.read().splitlines()
        if str(m.from_user.id) not in users:
            f.write(str(m.from_user.id) + "\n")
            bot.send_message(ADMIN_ID, f"👤 **New User Alert!**\nName: {m.from_user.first_name}\nUser: @{m.from_user.username}")

    if force_join_active and not is_member(m.from_user.id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Channel 📢", url=CHANNEL_LINK))
        markup.add(InlineKeyboardButton("Verify Subscription ✅", callback_data="check"))
        bot.send_message(m.chat.id, "⚠️ **Access Locked!**\n\nTo see live stats and predictions, you must join our official channel first.", 
                         reply_markup=markup, parse_mode="Markdown")
        return

    bot.send_message(m.chat.id, "⚽️ **Elite Football Analysis**\n\nSelect a service to get detailed data:", 
                     reply_markup=get_menu(), parse_mode="Markdown")

# الكود السري الجديد 8899898 لتفعيل/تعطيل القفل
@bot.message_handler(func=lambda m: m.text == '8899898' and m.from_user.id == ADMIN_ID)
def toggle_lock(m):
    global force_join_active
    force_join_active = not force_join_active
    status = "ON 🔴 (Locked)" if force_join_active else "OFF 🟢 (Open for Ads Review)"
    bot.reply_to(m, f"Subscription system is now: {status}")

@bot.message_handler(commands=['broadcast'], func=lambda m: m.from_user.id == ADMIN_ID)
def broadcast_init(m):
    msg = bot.reply_to(m, "Send the message (text/photo) you want to send to all users.")
    bot.register_next_step_handler(msg, broadcast_send)

def broadcast_send(m):
    with open(users_file, "r") as f:
        users = f.read().splitlines()
    count = 0
    for u in users:
        try:
            bot.copy_message(u, m.chat.id, m.message_id)
            count += 1
        except: pass
    bot.send_message(ADMIN_ID, f"✅ Broadcast finished. Sent to {count} users.")

@bot.callback_query_handler(func=lambda call: True)
def callback_logic(call):
    if call.data == "check":
        if is_member(call.from_user.id):
            bot.edit_message_text("✅ Access Granted! Choose a service:", call.message.chat.id, call.message.message_id, reply_markup=get_menu())
        else:
            bot.answer_callback_query(call.id, "❌ You haven't joined yet!", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "Data is being updated...")

# --- التشغيل النهائي ---
if __name__ == "__main__":
    # تشغيل سيرفر Flask لتفادي توقف Render
    threading.Thread(target=run_flask, daemon=True).start()
    print("Bot is starting...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
