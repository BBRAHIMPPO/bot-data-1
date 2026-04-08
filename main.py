import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
import time
import threading
import requests
from flask import Flask, request

# 🔐 CONFIGURATION - Use Render environment variables
BOT_TOKEN = os.environ.get('8744376397:AAFsFf-AsevpB-L5btSksOIUljvcai1HUCw')  # Get token from environment variable
ADMIN_ID = int(os.environ.get('ADMIN_ID', 19999))  # Get from env, default 19999
REQUIRED_CHANNEL = os.environ.get('REQUIRED_CHANNEL', 'https://t.me/+lIwJqGViEdg1YmU0')

DATA_FILE = 'bot_data.json'
# Flask app for web server (to keep Render happy)
app = Flask(__name__)

# ==============================================
# 📁 DATA MANAGEMENT
# ==============================================
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

# ==============================================
# 🛠️ HELPER FUNCTIONS
# ==============================================
def is_user_subscribed(user_id):
    """Check if user is subscribed to the required channel"""
    try:
        chat_member = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Subscription check error for {user_id}: {e}")
        # Return True only for testing without channel check
        return False

def is_admin(user_id):
    return user_id == ADMIN_ID

def save_new_user(user_id, username=None):
    if user_id not in bot_data['user_ids']:
        bot_data['user_ids'].append(user_id)
        save_data(bot_data)
        user_info = f"🆕 **New User!**\n👤 ID: `{user_id}`\n📝 @{username}" if username else f"🆕 **New User!**\n👤 ID: `{user_id}`"
        bot.send_message(ADMIN_ID, user_info, parse_mode='Markdown')

def create_main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    btn_stats1 = InlineKeyboardButton("⚽ Premier League", callback_data="stats_pl")
    btn_stats2 = InlineKeyboardButton("🏆 Champions League", callback_data="stats_ucl")
    btn_channel = InlineKeyboardButton("📢 Join Channel", url=bot_data['settings']['channel_link'])
    btn_admin = InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel")
    markup.add(btn_stats1, btn_stats2, btn_channel, btn_admin)
    return markup

# ==============================================
# 🤖 TELEGRAM BOT HANDLERS
# ==============================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username
    save_new_user(user_id, username)
    
    if is_user_subscribed(user_id):
        welcome_text = f"🎉 **Welcome {message.from_user.first_name}!**\n✅ You are subscribed.\n👇 Choose an option:"
        bot.send_message(message.chat.id, welcome_text, reply_markup=create_main_menu(), parse_mode='Markdown')
    else:
        text = f"⚠️ **Access Denied, {message.from_user.first_name}**\n\nYou must join our channel first.\n🔔 Click below & press Verify."
        markup = InlineKeyboardMarkup()
        btn_channel = InlineKeyboardButton("📢 Join Channel", url=bot_data['settings']['channel_link'])
        btn_verify = InlineKeyboardButton("✅ Verify", callback_data="verify")
        markup.add(btn_channel, btn_verify)
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if is_admin(message.from_user.id):
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
                   InlineKeyboardButton("⚙️ Channel Link", callback_data="admin_settings"),
                   InlineKeyboardButton("👥 Users List", callback_data="admin_users"),
                   InlineKeyboardButton("📊 Stats", callback_data="admin_stats"))
        bot.send_message(message.chat.id, "👑 **Admin Panel**", reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "⛔ Unauthorized.")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    
    if call.data == "verify":
        if is_user_subscribed(user_id):
            bot.edit_message_text("✅ Verified! Welcome.", call.message.chat.id, call.message.id)
            bot.send_message(call.message.chat.id, "Main menu:", reply_markup=create_main_menu())
        else:
            bot.answer_callback_query(call.id, "❌ Not subscribed yet.", show_alert=True)
    
    elif call.data.startswith("stats_"):
        if is_user_subscribed(user_id):
            match = call.data.split("_")[1]
            if match == "pl":
                stats = "⚽ **Premier League Stats**\nTop scorer: Haaland (21)\nPossession: Man City 65%"
            else:
                stats = "🏆 **UCL Stats**\nTop scorer: Mbappé (8)\nAssists: Vinicius Jr (5)"
            bot.send_message(call.message.chat.id, stats, parse_mode='Markdown')
            bot.answer_callback_query(call.id, "📊 Stats loaded")
        else:
            bot.answer_callback_query(call.id, "❌ Subscribe first.", show_alert=True)
    
    elif call.data == "admin_panel":
        if is_admin(user_id):
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
                       InlineKeyboardButton("⚙️ Channel Link", callback_data="admin_settings"),
                       InlineKeyboardButton("👥 Users", callback_data="admin_users"),
                       InlineKeyboardButton("📊 Stats", callback_data="admin_stats"))
            bot.edit_message_text("👑 Admin Panel", call.message.chat.id, call.message.id, reply_markup=markup)
    
    elif call.data == "admin_broadcast":
        if is_admin(user_id):
            bot.send_message(call.message.chat.id, "Send the message to broadcast. (Type /cancel to abort)")
            bot.register_next_step_handler(call.message, broadcast_message)
    
    elif call.data == "admin_settings":
        if is_admin(user_id):
            bot.send_message(call.message.chat.id, "Send new channel invite link (e.g., https://t.me/+xxxx)")
            bot.register_next_step_handler(call.message, update_channel_link)
    
    elif call.data == "admin_users":
        if is_admin(user_id):
            users = "\n".join([f"👤 `{uid}`" for uid in bot_data['user_ids'][:30]])
            bot.send_message(call.message.chat.id, f"👥 **Users** ({len(bot_data['user_ids'])} total):\n{users}", parse_mode='Markdown')
    
    elif call.data == "admin_stats":
        if is_admin(user_id):
            bot.send_message(call.message.chat.id, f"📊 **Bot Stats**\n👥 Users: {len(bot_data['user_ids'])}\n🔗 Link: {bot_data['settings']['channel_link']}")

def broadcast_message(message):
    if message.text == "/cancel":
        bot.send_message(message.chat.id, "Broadcast cancelled.")
        return
    msg = message.text
    success = 0
    for uid in bot_data['user_ids']:
        try:
            bot.send_message(uid, f"📢 **Announcement**\n\n{msg}", parse_mode='Markdown')
            success += 1
            time.sleep(0.05)
        except:
            pass
    bot.send_message(message.chat.id, f"✅ Broadcast sent to {success} users.")

def update_channel_link(message):
    if message.text == "/cancel":
        bot.send_message(message.chat.id, "Cancelled.")
        return
    bot_data['settings']['channel_link'] = message.text.strip()
    save_data(bot_data)
    bot.send_message(message.chat.id, f"✅ Channel link updated to: {message.text}")

# ==============================================
# 🌐 FLASK WEB SERVER (to keep Render happy)
# ==============================================
@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

# ==============================================
# 🚀 RUN BOT IN SEPARATE THREAD
# ==============================================
def run_bot():
    """Run Telegram bot in a separate thread"""
    print("🤖 Starting Telegram bot...")
    bot.infinity_polling(skip_pending=True)

if __name__ == '__main__':
    # Start Telegram bot in background thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Get port from Render environment
    port = int(os.environ.get('PORT', 5000))
    
    # Start Flask web server
    print(f"🌐 Starting web server on port {port}...")
    app.run(host='0.0.0.0', port=port)
