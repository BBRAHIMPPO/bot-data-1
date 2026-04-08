import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading
import os

# --- الإعدادات (تأكد من ملء هذه البيانات) ---
TOKEN = "8744376397:AAFsFf-AsevpB-L5btSksOIUljvcai1HUCw"
ADMIN_ID = 000000000  # 👈 حط الـ ID ديالك هنا ضروري باش تخدم لوحة التحكم
CHANNEL_ID = "-1002264628286" 
CHANNEL_LINK = "https://t.me/+lIwJqGViEdg1YmU0"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ملف حفظ المستخدمين
users_file = "database.txt"
if not os.path.exists(users_file):
    with open(users_file, "w") as f: pass

# حالة القفل (OFF للمراجعة الإعلانية، ON بعد القبول)
force_join_active = False 

# --- نظام Flask لتجاوز مشاكل Render ---
@app.route('/')
def health_check():
    return "Bot and Admin Panel are running perfectly!", 200

# --- وظائف التحقق للمستخدمين ---
def is_member(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def get_user_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    options = [
        "Live Scores ⚽️", "Predictions 📈", "Match Stats 📊", "H2H Results ⚔️",
        "Lineups 🏟", "League Tables 📅", "Transfer News 📰", "Top Scorers 🏆",
        "Injury Updates 🚑", "Referee Stats 🏁", "Corner Stats 🚩", "Card Stats 🟨",
        "Odds Analysis 🎰", "Stadium Info 📍", "TV Channels 📺", "Daily Tips 💡",
        "Player Ratings ⭐", "Value Bets 💰", "VIP Insights 💎", "Support 🛠"
    ]
    buttons = [InlineKeyboardButton(opt, callback_data="user_info") for opt in options]
    markup.add(*buttons)
    return markup

# --- رسالة البداية للمستخدمين ---
@bot.message_handler(commands=['start'])
def welcome(m):
    # تسجيل المستخدم 
    with open(users_file, "r+") as f:
        users = f.read().splitlines()
        if str(m.from_user.id) not in users:
            f.write(str(m.from_user.id) + "\n")
            bot.send_message(ADMIN_ID, f"👤 **New User Alert!**\nName: {m.from_user.first_name}\nUser: @{m.from_user.username}")

    if force_join_active and not is_member(m.from_user.id) and m.from_user.id != ADMIN_ID:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Channel 📢", url=CHANNEL_LINK))
        markup.add(InlineKeyboardButton("Verify Subscription ✅", callback_data="check_join"))
        bot.send_message(m.chat.id, "⚠️ **Access Locked!**\n\nTo see live stats and predictions, you must join our official channel first.", 
                         reply_markup=markup, parse_mode="Markdown")
        return

    bot.send_message(m.chat.id, "⚽️ **Elite Football Analysis**\n\nSelect a service to get detailed data:", 
                     reply_markup=get_user_menu(), parse_mode="Markdown")

# ==========================================
#         🛠 لوحة تحكم الأدمن (Admin Panel) 🛠
# ==========================================

def get_admin_panel():
    markup = InlineKeyboardMarkup(row_width=2)
    # حالة زر الاشتراك الاجباري
    status_text = "🔒 Force Join: ON (Locked)" if force_join_active else "🔓 Force Join: OFF (Ads Mode)"
    
    btn_toggle = InlineKeyboardButton(status_text, callback_data="admin_toggle")
    btn_stats = InlineKeyboardButton("📊 Users Stats", callback_data="admin_stats")
    btn_broadcast = InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
    
    markup.add(btn_toggle)
    markup.add(btn_stats, btn_broadcast)
    return markup

@bot.message_handler(func=lambda m: m.text == '998899' and m.from_user.id == ADMIN_ID)
def open_admin_panel(m):
    bot.send_message(m.chat.id, "⚙️ **Welcome to Admin Panel**\nChoose an action below:", 
                     reply_markup=get_admin_panel(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_callbacks(call):
    global force_join_active
    
    if call.data == "admin_toggle":
        force_join_active = not force_join_active
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_admin_panel())
        bot.answer_callback_query(call.id, "System updated!")
        
    elif call.data == "admin_stats":
        with open(users_file, "r") as f:
            count = len(f.read().splitlines())
        bot.answer_callback_query(call.id, f"👥 Total Users: {count}", show_alert=True)
        
    elif call.data == "admin_broadcast":
        msg = bot.send_message(call.message.chat.id, "✍️ Send the message or photo you want to broadcast to all users (Type 'cancel' to stop):")
        bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(m):
    if m.text and m.text.lower() == 'cancel':
        bot.send_message(m.chat.id, "❌ Broadcast cancelled.")
        return
        
    bot.send_message(m.chat.id, "⏳ Sending broadcast...")
    with open(users_file, "r") as f:
        users = f.read().splitlines()
    
    count = 0
    for u in users:
        try:
            bot.copy_message(u, m.chat.id, m.message_id)
            count += 1
        except: pass
    
    bot.send_message(m.chat.id, f"✅ Broadcast successfully sent to {count} users.")

# ==========================================
#         معالجة أزرار المستخدم العادي
# ==========================================
@bot.callback_query_handler(func=lambda call: not call.data.startswith("admin_"))
def user_callbacks(call):
    if call.data == "check_join":
        if is_member(call.from_user.id):
            bot.edit_message_text("✅ Access Granted! Choose a service:", call.message.chat.id, call.message.message_id, reply_markup=get_user_menu())
        else:
            bot.answer_callback_query(call.id, "❌ You haven't joined yet!", show_alert=True)
    elif call.data == "user_info":
        bot.answer_callback_query(call.id, "Data is being updated...")

# --- التشغيل النهائي (Background Bot + Foreground Web) ---
def run_bot():
    try:
        print("Bot is polling...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Bot polling error: {e}")

if __name__ == "__main__":
    # 1. تشغيل البوت في الخلفية باش ما يحبسش Render
    threading.Thread(target=run_bot, daemon=True).start()
    
    # 2. تشغيل Flask في الواجهة باش Render يلقى الـ Port
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting web server on port {port}...")
    app.run(host='0.0.0.0', port=port)
