import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
import time
import threading
from flask import Flask

# ---------- بيانات الإعدادات (غيّرها وفقاً لبياناتك) ----------
BOT_TOKEN = '8744376397:AAFsFf-AsevpB-L5btSksOIUljvcai1HUCw'
ADMIN_ID = 19999
REQUIRED_CHANNEL = '@lIwJqGViEdg1YmU0'
# ---------------------------------------------------------

DATA_FILE = 'bot_data.json'
app = Flask(__name__)

# تحميل وحفظ بيانات المستخدمين
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {'user_ids': [], 'settings': {'channel_link': 'https://t.me/+lIwJqGViEdg1YmU0'}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

bot_data = load_data()
bot = telebot.TeleBot(BOT_TOKEN)

# ---------- وظائف البوت الأساسية ----------
def is_user_subscribed(user_id):
    """تتحقق من اشتراك المستخدم في القناة"""
    try:
        chat_member = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"خطأ في التحقق من الاشتراك للمستخدم {user_id}: {e}")
        return False

def is_admin(user_id):
    return user_id == ADMIN_ID

def save_new_user(user_id, username=None):
    if user_id not in bot_data['user_ids']:
        bot_data['user_ids'].append(user_id)
        save_data(bot_data)
        user_info = f"🆕 **مستخدم جديد!**\nID: `{user_id}`\nUsername: @{username}" if username else f"🆕 **مستخدم جديد!**\nID: `{user_id}`"
        bot.send_message(ADMIN_ID, user_info, parse_mode='Markdown')

def create_main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    btn_stats1 = InlineKeyboardButton("⚽ إحصائيات الدوري الإنجليزي", callback_data="stats_pl")
    btn_stats2 = InlineKeyboardButton("🏆 إحصائيات دوري الأبطال", callback_data="stats_ucl")
    btn_channel = InlineKeyboardButton("📢 انضم للقناة", url=bot_data['settings']['channel_link'])
    btn_admin = InlineKeyboardButton("👑 لوحة التحكم", callback_data="admin_panel")
    markup.add(btn_stats1, btn_stats2, btn_channel, btn_admin)
    return markup

def get_live_match_stats(match_type):
    """تجلب الإحصائيات (يمكنك استبدالها بـ API حقيقي)"""
    if match_type == "pl":
        return ("⚽ **إحصائيات حية - الدوري الإنجليزي**\n\n"
                "مانشستر سيتي 2 - 0 ليفربول\n"
                "⚽️ الأهداف: هالاند (د21)، فودين (د55)\n"
                "🟨 بطاقات صفراء: 1 (ليفربول)\n"
                "⏱️ الاستحواذ: 58% - 42%")
    elif match_type == "ucl":
        return ("🏆 **إحصائيات حية - دوري أبطال أوروبا**\n\n"
                "ريال مدريد 1 - 1 بايرن ميونخ\n"
                "⚽️ الأهداف: فينيسيوس (د35)، كين (د70)\n"
                "🟨 بطاقات صفراء: 2 (مدريد)، 1 (بايرن)\n"
                "⏱️ الاستحواذ: 52% - 48%")
    else:
        return "📊 لا توجد بيانات لهذه المباراة."

# ---------- أوامر البوت ----------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username
    save_new_user(user_id, username)

    if is_user_subscribed(user_id):
        welcome_text = f"🎉 **أهلاً بك {message.from_user.first_name}!**\n✅ أنت مشترك في القناة.\n👇 اختر الخيار المناسب:"
        bot.send_message(message.chat.id, welcome_text, reply_markup=create_main_menu(), parse_mode='Markdown')
    else:
        text = f"⚠️ **عذراً, {message.from_user.first_name}**\n\nيجب عليك الاشتراك في قناتنا أولاً.\n🔔 اضغط على الزر أدناه للاشتراك ثم اضغط 'تحقق'."
        markup = InlineKeyboardMarkup()
        btn_channel = InlineKeyboardButton("📢 انضم للقناة", url=bot_data['settings']['channel_link'])
        btn_verify = InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="verify")
        markup.add(btn_channel, btn_verify)
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if is_admin(message.from_user.id):
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("📢 رسالة جماعية", callback_data="admin_broadcast"),
                   InlineKeyboardButton("⚙️ رابط القناة", callback_data="admin_settings"),
                   InlineKeyboardButton("👥 عرض المستخدمين", callback_data="admin_users"),
                   InlineKeyboardButton("📊 إحصائيات البوت", callback_data="admin_stats"))
        bot.send_message(message.chat.id, "👑 **لوحة تحكم المدير**", reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "⛔ غير مصرح لك باستخدام هذا الأمر.")

# ---------- معالجة الأزرار ----------
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id

    if call.data == "verify":
        if is_user_subscribed(user_id):
            bot.edit_message_text("✅ **تم التحقق بنجاح! مرحباً بك.**", call.message.chat.id, call.message.id, parse_mode='Markdown')
            bot.send_message(call.message.chat.id, "القائمة الرئيسية:", reply_markup=create_main_menu())
        else:
            bot.answer_callback_query(call.id, "❌ لم تشترك بعد. الرجاء الاشتراك أولاً.", show_alert=True)

    elif call.data.startswith("stats_"):
        if is_user_subscribed(user_id):
            match = call.data.split("_")[1]
            stats = get_live_match_stats(match)
            bot.send_message(call.message.chat.id, stats, parse_mode='Markdown')
            bot.answer_callback_query(call.id, "📊 جاري تحميل الإحصائيات...")
        else:
            bot.answer_callback_query(call.id, "❌ الرجاء الاشتراك في القناة أولاً.", show_alert=True)

    elif call.data == "admin_panel":
        if is_admin(user_id):
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(InlineKeyboardButton("📢 رسالة جماعية", callback_data="admin_broadcast"),
                       InlineKeyboardButton("⚙️ رابط القناة", callback_data="admin_settings"),
                       InlineKeyboardButton("👥 عرض المستخدمين", callback_data="admin_users"),
                       InlineKeyboardButton("📊 إحصائيات البوت", callback_data="admin_stats"))
            bot.edit_message_text("👑 **لوحة تحكم المدير**", call.message.chat.id, call.message.id, reply_markup=markup, parse_mode='Markdown')

    elif call.data == "admin_broadcast":
        if is_admin(user_id):
            bot.send_message(call.message.chat.id, "📢 **أرسل الرسالة التي تريد نشرها لجميع المستخدمين.** (اكتب /cancel للإلغاء)")
            bot.register_next_step_handler(call.message, broadcast_message)

    elif call.data == "admin_settings":
        if is_admin(user_id):
            bot.send_message(call.message.chat.id, "⚙️ **أرسل رابط دعوة القناة الجديد.** (مثال: https://t.me/+XXXXXXXXXX)")
            bot.register_next_step_handler(call.message, update_channel_link)

    elif call.data == "admin_users":
        if is_admin(user_id):
            users = "\n".join([f"👤 `{uid}`" for uid in bot_data['user_ids'][:30]])
            total = len(bot_data['user_ids'])
            bot.send_message(call.message.chat.id, f"👥 **قائمة المستخدمين**\nالإجمالي: {total}\n\n{users}", parse_mode='Markdown')

    elif call.data == "admin_stats":
        if is_admin(user_id):
            total = len(bot_data['user_ids'])
            bot.send_message(call.message.chat.id, f"📊 **إحصائيات البوت**\n👥 إجمالي المستخدمين: {total}\n🔗 رابط القناة: {bot_data['settings']['channel_link']}")

def broadcast_message(message):
    if message.text == "/cancel":
        bot.send_message(message.chat.id, "❌ تم إلغاء النشر.")
        return
    msg = message.text
    success = 0
    for uid in bot_data['user_ids']:
        try:
            bot.send_message(uid, f"📢 **إعلان هام**\n\n{msg}", parse_mode='Markdown')
            success += 1
            time.sleep(0.05)
        except:
            pass
    bot.send_message(message.chat.id, f"✅ تم إرسال الرسالة إلى {success} مستخدم.")

def update_channel_link(message):
    if message.text == "/cancel":
        bot.send_message(message.chat.id, "❌ تم الإلغاء.")
        return
    new_link = message.text.strip()
    bot_data['settings']['channel_link'] = new_link
    save_data(bot_data)
    bot.send_message(message.chat.id, f"✅ تم تحديث رابط القناة إلى: {new_link}")

# ---------- نقطة الصحة (Health Check) لـ Render ----------
@app.route('/health')
def health_check():
    """هذه النقطة هي التي ستمنع البوت من التوقف على Render"""
    return "البوت يعمل بشكل طبيعي", 200

def run_bot():
    """تشغيل البوت في thread منفصل"""
    print("🤖 جاري تشغيل بوت تيليجرام...")
    bot.infinity_polling(skip_pending=True)

if __name__ == '__main__':
    # بدء تشغيل البوت في thread منفصل حتى لا يتعارض مع Flask
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # تشغيل خادم Flask الصغير
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 جاري تشغيل نقطة الصحة (Health Check) على المنفذ {port}...")
    app.run(host='0.0.0.0', port=port)
