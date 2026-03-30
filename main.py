import threading
import time
import random
import io
import os
from flask import Flask
import telebot
from PIL import Image, ImageDraw, ImageFont

# --- إعداد Flask لـ Render ---
app = Flask(__name__)
@app.route('/')
def home(): return "Image Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- إعدادات البوت ---
TOKEN = '8762517288:AAFPSd4rv5z5RZRv8xHABt4ALcC25fMpoBA'
bot = telebot.TeleBot(TOKEN)

def generate_score_and_odds():
    possible_scores = [(h, a) for h in range(7) for a in range(7)]
    home, away = random.choice(possible_scores)
    score_str = f"{home} - {away}"
    total = home + away
    
    if total == 0: odds = round(random.uniform(9.0, 11.0), 2)
    elif total <= 2: odds = round(random.uniform(12.0, 18.0), 2)
    elif total <= 4: odds = round(random.uniform(19.0, 30.0), 2)
    elif total <= 7: odds = round(random.uniform(31.0, 42.0), 2)
    else: odds = round(random.uniform(43.0, 50.0), 2)
    return score_str, odds

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        img = Image.open(io.BytesIO(downloaded_file))
        draw = ImageDraw.Draw(img)
        
        score, odds = generate_score_and_odds()
        overlay_text = f"FIXED: {score}\nODDS: {odds}"
        
        try:
            # في Linux/Render غالباً ما كيكونش Arial، كنستعملو هاد الطريقة
            font = ImageFont.load_default() 
        except:
            font = None

        # كتابة النص باللون الأخضر
        draw.text((25, 25), overlay_text, fill=(0, 255, 0), font=font)

        output = io.BytesIO()
        img.save(output, format='PNG')
        output.seek(0)

        caption_text = f"✅ **100% Real Information**\n\nTip : Correct Score ( {score} ) FT\nOdd : {odds}\n\nThis Match Is 100% Safe And Guaranteed"
        
        bot.send_photo(message.chat.id, output, caption=caption_text, parse_mode='Markdown')

    except Exception as e:
        print(f"Error: {e}")

# --- تشغيل البوت مع Flask ---
if __name__ == "__main__":
    # تشغيل Flask في Thread منفصل
    threading.Thread(target=run_flask).start()
    print("🤖 Bot is ready and Flask is running...")
    bot.infinity_polling()
