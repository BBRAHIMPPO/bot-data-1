import telebot
from PIL import Image, ImageDraw, ImageFont
import random
import io

# التوكن الخاص بك
TOKEN = '8762517288:AAFPSd4rv5z5RZRv8xHABt4ALcC25fMpoBA'
bot = telebot.TeleBot(TOKEN)

def generate_score_and_odds():
    # إنشاء قائمة بجميع النتائج الممكنة من 0-0 لـ 6-6
    possible_scores = []
    for home in range(7):
        for away in range(7):
            possible_scores.append((home, away))
    
    # اختيار نتيجة واحدة عشوائياً من القائمة
    home, away = random.choice(possible_scores)
    score_str = f"{home} - {away}"
    
    # حساب الـ Odds بناءً على مجموع الأهداف
    total_goals = home + away
    
    if total_goals == 0: # 0-0
        odds = round(random.uniform(9.0, 11.0), 2)
    elif total_goals <= 2: # مجموع أهداف قليل
        odds = round(random.uniform(12.0, 18.0), 2)
    elif total_goals <= 4: # مجموع أهداف متوسط
        odds = round(random.uniform(19.0, 30.0), 2)
    elif total_goals <= 7: # أهداف كثيرة
        odds = round(random.uniform(31.0, 42.0), 2)
    else: # نتائج كبيرة بحال 5-5 أو 6-6
        odds = round(random.uniform(43.0, 50.0), 2)
        
    return score_str, odds

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # تحميل الصورة اللي صيفطتي
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # تعديل الصورة بـ Pillow
        img = Image.open(io.BytesIO(downloaded_file))
        draw = ImageDraw.Draw(img)
        
        # الحصول على النتيجة والـ Odds
        score, odds = generate_score_and_odds()
        
        # النص اللي غيتكتب فوق الصورة
        overlay_text = f"FIXED: {score}\nODDS: {odds}"
        
        # اختيار الخط (إلا مكنش arial غيخدم بالافتراضي)
        try:
            font = ImageFont.truetype("arial.ttf", 50) # كبّرت الخط لـ 50 باش يبان واضح
        except:
            font = ImageFont.load_default()

        # كتابة النص (الإحداثيات 20, 20 تقدر تبدلها على حساب فين بغيتيها تبان)
        # اللون الأخضر (0, 255, 0) كيبان مزيان في أوراق اللعب
        draw.text((20, 20), overlay_text, fill=(0, 255, 0), font=font)

        # تحويل الصورة المعدلة لإرسالها
        output = io.BytesIO()
        img.save(output, format='PNG')
        output.seek(0)

        # الـ Caption اللي طلبتي
        caption_text = f"""
100 % Real Information

Tip : Correct Score ( {score} ) FT
 
Odd : {odds}

This Match Is 100% Safe And it’s Trusted And Guaranteed

Available on all betting sites 🤝
"""
        
        bot.send_photo(message.chat.id, output, caption=caption_text, parse_mode='Markdown')

    except Exception as e:
        print(f"Error: {e}")

print("Bot is ready...")
bot.infinity_polling()
