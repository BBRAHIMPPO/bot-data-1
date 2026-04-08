import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

# المعطيات الخاصة بك
TOKEN = "8744376397:AAFsFf-AsevpB-L5btSksOIUljvcai1HUCw"
# ملاحظة: بالنسبة للقنوات الخاصة، يفضل وضع الـ ID الخاص بالقناة (يبدأ بـ -100)
# سأستخدم رابط الدعوة الذي قدمته في أزرار الاشتراك
CHANNEL_INVITE = "https://t.me/+lIwJqGViEdg1YmU0"
ADMIN_ID = 000000000  # 👈 ضروري: حط الـ ID ديالك هنا باش يخدم ليك الكود 7799 و الإذاعة

bot = telebot.TeleBot(TOKEN)

# تخزين المستخدمين في ملف نصي بسيط
users_file = "database.txt"
if not os.path.exists(users_file):
    with open(users_file, "w") as f: pass

# حالة قفل القناة (تبدأ بـ False لضمان قبول الإعلان)
force_join_active = False

def add_user_to_db(user_id):
    with open(users_file, "r+") as f:
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(str(user_id) + "\n")
            return True
    return False

# دالة التحقق من الاشتراك (مهم: البوت يجب أن يكون "Admin" في القناة)
def is_subscribed(user_id):
    try:
        # ملاحظة: في القنوات الخاصة، التحقق يتطلب معرفة ID القناة. 
        # إذا واجهت مشكلة، تأكد من إضافة البوت كـ Admin في القناة أولاً.
        status = bot.get_chat_member("-1002264628286", user_id).status # ستحتاج لتغيير هذا للـ ID الفعلي لقناتك
        return status in ['member', 'administrator', 'creator']
    except:
        # في حالة القنوات الخاصة جداً، قد يرجع خطأ، سنفترض أنه غير مشترك ليظهر له الزر
        return False

# قائمة الـ 20 اختيار بالإنجليزية لإعطاء طابع احترافي (Ads Friendly)
def get_main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    options = [
        "Live Scores ⚽️", "Predictions 📈", "Match Stats 📊", "H2H Results ⚔️",
        "Lineups 🏟", "League Tables 📅", "Top Scorers 🏆", "Transfer News 📰",
        "Injury List 🚑", "Referee Stats 🏁", "Corner Stats 🚩", "Card Stats 🟨",
        "Odds Analysis 🎰", "Stadium Guide 📍", "TV Channels 📺", "Daily Tips 💡",
        "Player Ratings ⭐", "Value Bets 💰", "VIP Insights 💎", "Support 🛠"
    ]
    buttons = [InlineKeyboardButton(opt, callback_data="feature_info") for opt in options]
    markup.add(*buttons)
    return markup

# --- أوامر الأدمن ---

@bot.message_handler(func=lambda m: m.text == '7799' and m.from_user.id == ADMIN_ID)
def secret_toggle(m):
    global force_join_active
    force_join_active = not force_join_active
    status = "ACTIVATED 🔴" if force_join_active else "DEACTIVATED 🟢"
    bot.reply_to(m, f"Subscription Lock is now {status}.\nNew users must join the channel: {force_join_active}")

@bot.message_handler(commands=['broadcast'], func=lambda m: m.from_user.id == ADMIN_ID)
def start_broadcast(m):
    msg = bot.reply_to(m, "Send me the message (Text/Photo) you want to broadcast to everyone.")
    bot.register_next_step_handler(msg, do_broadcast)

def do_broadcast(m):
    with open(users_file, "r") as f:
        users = f.read().splitlines()
    success = 0
    for user in users:
        try:
            bot.copy_message(user, m.chat.id, m.message_id)
            success += 1
        except: pass
    bot.send_message(ADMIN_ID, f"✅ Done! Broadcast sent to {success} users.")

# --- المعالجة الأساسية ---

@bot.message_handler(commands=['start'])
def welcome(m):
    is_new = add_user_to_db(m.from_user.id)
    
    # تنبيه الأدمن بمستخدم جديد
    if is_new:
        bot.send_message(ADMIN_ID, f"🔔 New User: {m.from_user.first_name} (@{m.from_user.username})\nTotal users stored: {len(open(users_file).readlines())}")

    # نظام القفل
    if force_join_active and not is_subscribed(m.from_user.id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Channel 📢", url=CHANNEL_INVITE))
        markup.add(InlineKeyboardButton("Verify ✅", callback_data="verify_sub"))
        bot.send_message(m.chat.id, "⚠️ **Access Denied!**\n\nPlease join our official channel to unlock the football statistics bot.", 
                         reply_markup=markup, parse_mode="Markdown")
        return

    # الواجهة العادية (تظهر للمراجعين وللمشتركين)
    bot.send_message(m.chat.id, "⚽️ **Welcome to Elite Football Stats**\nSelect a service to get detailed analytics:", 
                     reply_markup=get_main_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    if call.data == "verify_sub":
        if is_subscribed(call.from_user.id):
            bot.answer_callback_query(call.id, "Success! Welcome.")
            bot.edit_message_text("✅ Access Granted! Choose a service:", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu())
        else:
            bot.answer_callback_query(call.id, "❌ You haven't joined the channel yet!", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "This data is updating... Please wait.")

print("Bot is starting...")
bot.infinity_polling()
