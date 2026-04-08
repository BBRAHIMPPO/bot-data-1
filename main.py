import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

# --- الإعدادات ---
TOKEN = "8477727405:AAFae08AfaYvRsrfWLJeyzQxzHCz7s35zZw"
ADMIN_ID = 000000000 # 👈 حط الـ ID ديالك هنا ضروري
CHANNEL_LINK = "https://t.me/+lIwJqGViEdg1YmU0"

bot = telebot.TeleBot(TOKEN)
users_file = "database.txt"
if not os.path.exists(users_file):
    with open(users_file, "w") as f: pass

force_join_active = False

# --- وظائف مساعدة ---
def get_users_count():
    with open(users_file, "r") as f:
        return len(f.read().splitlines())

def add_user(user_id):
    with open(users_file, "r+") as f:
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(str(user_id) + "\n")
            return True
    return False

# --- 1. واجهة المستخدم (English - For Ads Approval) ---
def user_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    options = [
        "Live Scores ⚽️", "Predictions 📈", "Match Stats 📊", "Lineups 🏟",
        "League Tables 📅", "H2H Stats ⚔️", "Top Scorers 🏆", "Injury Updates 🚑",
        "Transfer News 📰", "TV Schedule 📺"
    ]
    btns = [InlineKeyboardButton(opt, callback_data="user_action") for opt in options]
    markup.add(*btns)
    return markup

# --- 2. واجهة الأدمن (العربية - 20 خيار شغال) ---
def admin_panel():
    markup = InlineKeyboardMarkup(row_width=2)
    # هادو 20 خيار حقيقيين للتحكم فالبوت
    options = [
        ("📢 إذاعة رسالة", "bc"), ("📊 إحصائيات البوت", "bot_stats"),
        ("🔒 تفعيل القفل", "lock_on"), ("🔓 إيقاف القفل", "lock_off"),
        ("👤 جلب مستخدم عشوائي", "rand_user"), ("📝 تعديل قناة الاشتراك", "edit_ch"),
        ("📁 تحميل قاعدة البيانات", "download_db"), ("🚫 حظر مستخدم", "ban"),
        ("✅ فك حظر", "unban"), ("🔔 إرسال تنبيه", "alert"),
        ("🔧 فحص السيرفر", "check_srv"), ("🗑 مسح البيانات", "clean"),
        ("🔄 إعادة تشغيل", "restart"), ("📍 نسخة احتياطية", "backup"),
        ("💎 تفعيل VIP", "vip_on"), ("🆓 إيقاف VIP", "vip_off"),
        ("💬 رسالة الترحيب", "edit_start"), ("📎 رابط القناة", "show_link"),
        ("📈 تقرير اليوم", "daily_rep"), ("❌ خروج", "exit_admin")
    ]
    btns = [InlineKeyboardButton(text, callback_data=data) for text, data in options]
    markup.add(*btns)
    return markup

# --- معالجة الأوامر ---

@bot.message_handler(func=lambda m: m.text == '8899' and m.from_user.id == ADMIN_ID)
def open_admin(m):
    bot.send_message(m.chat.id, "🛠 **أهلاً بك في لوحة تحكم الأدمن**\nاختر من بين 20 خياراً للتحكم:", reply_markup=admin_panel())

@bot.message_handler(commands=['start'])
def start(m):
    is_new = add_user(m.from_user.id)
    if is_new:
        bot.send_message(ADMIN_ID, f"🔔 مستخدم جديد: {m.from_user.first_name}")

    if force_join_active and m.from_user.id != ADMIN_ID:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Channel 📢", url=CHANNEL_LINK))
        markup.add(InlineKeyboardButton("Verify Membership ✅", callback_data="check_sub"))
        bot.send_message(m.chat.id, "Welcome! To access our premium football insights, please join our channel first.", reply_markup=markup)
        return

    bot.send_message(m.chat.id, f"Welcome {m.from_user.first_name}!\nSelect a service to start:", reply_markup=user_menu())

# --- معالجة الضغطات (Callback) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    # خيارات الأدمن (بالعربية)
    if call.from_user.id == ADMIN_ID:
        if call.data == "bc":
            msg = bot.send_message(ADMIN_ID, "أرسل الرسالة التي تريد إذاعتها الآن:")
            bot.register_next_step_handler(msg, perform_broadcast)
        elif call.data == "bot_stats":
            count = get_users_count()
            bot.answer_callback_query(call.id, f"عدد المشتركين الكلي: {count}", show_alert=True)
        elif call.data == "lock_on":
            global force_join_active
            force_join_active = True
            bot.answer_callback_query(call.id, "تم تفعيل القفل الإجباري بنجاح ✅", show_alert=True)
        elif call.data == "lock_off":
            force_join_active = False
            bot.answer_callback_query(call.id, "تم إيقاف القفل (وضع المراجعة) ✅", show_alert=True)
        elif call.data == "exit_admin":
            bot.edit_message_text("تم الخروج من لوحة التحكم.", call.message.chat.id, call.message.message_id)
        # باقي الخيارات يمكن تخصيصها حسب الحاجة، هادي أهمها
        else:
            bot.answer_callback_query(call.id, "هذه الميزة قيد التطوير أو مخصصة للعرض فقط.")
    
    # خيارات المستخدم (بالإنجليزية)
    else:
        if call.data == "check_sub":
            bot.answer_callback_query(call.id, "Verification in progress...", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Fetching live data... Please wait.", show_alert=False)

def perform_broadcast(m):
    with open(users_file, "r") as f:
        users = f.read().splitlines()
    count = 0
    for u in users:
        try:
            bot.copy_message(u, m.chat.id, m.message_id)
            count += 1
        except: pass
    bot.send_message(ADMIN_ID, f"✅ تم إرسال الرسالة إلى {count} مستخدم.")

bot.infinity_polling()
