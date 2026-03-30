import threading
import time
import random
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import telebot

# --- الإعدادات ---
TOKEN = "8678424700:AAFSt9OSJCvz9kFGJBxskW74a-euN4Oe994"
bot = telebot.TeleBot(TOKEN)

is_running = False
seen_links = set()

def get_driver():
    """إعداد المتصفح لبيئة السيرفر (Linux/Render)"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # إخفاء هوية البوت
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def scrape_logic(chat_id):
    global is_running
    driver = None
    keywords = ["correct score", "fixed match", "1-0 full time", "betting codes"]

    while is_running:
        try:
            if not driver:
                driver = get_driver()
            
            for word in keywords:
                if not is_running: break
                
                print(f"🔎 Searching for: {word}")
                driver.get(f"https://www.threads.net/search?q={word}")
                time.sleep(random.uniform(6, 10)) # محاكاة تفكير الإنسان

                # سكرول ذكي
                body = driver.find_element(By.TAG_NAME, 'body')
                for _ in range(3):
                    body.send_keys(Keys.PAGE_DOWN)
                    time.sleep(random.uniform(2, 4))

                # جلب البروفايلات
                profiles = driver.find_elements(By.XPATH, "//a[contains(@href, '/@')]")
                profile_urls = list(set([p.get_attribute('href') for p in profiles]))

                for profile in profile_urls:
                    if not is_running: break
                    try:
                        driver.get(profile)
                        time.sleep(random.uniform(4, 7))
                        
                        links = driver.find_elements(By.TAG_NAME, 'a')
                        for l in links:
                            href = l.get_attribute('href')
                            if href and ('t.me/' in href or 'telegram.me' in href):
                                if href not in seen_links:
                                    bot.send_message(chat_id, f"🎯 Found Telegram:\n🔗 {href}")
                                    seen_links.add(href)
                                    print(f"✅ Sent: {href}")
                                    time.sleep(1)
                    except:
                        continue # كمل للبروفايل اللي موراه إلا وقع مشكل
                
            print("💤 Taking a short break...")
            time.sleep(300) # ارتاح 5 دقايق باش المنصة ما تعيقش

        except Exception as e:
            print(f"⚠️ Error: {e}. Restarting browser...")
            if driver:
                driver.quit()
            driver = None # كيعاود يفتح متصفح جديد في الدورة الجاية
            time.sleep(10)

@bot.message_handler(func=lambda m: m.text == "999")
def start_bot(message):
    global is_running
    if not is_running:
        is_running = True
        bot.reply_to(message, "🚀 السكريبت خدام دابا 100% وبلا مشاكل. غيوصلوك الروابط هنا.")
        threading.Thread(target=scrape_logic, args=(message.chat.id,)).start()
    else:
        bot.send_message(message.chat.id, "البوت خدام أصلاً!")

@bot.message_handler(func=lambda m: m.text == "000")
def stop_bot(message):
    global is_running
    is_running = False
    bot.reply_to(message, "🛑 توقف السكريبت.")

print("🤖 Waiting for '999' on Telegram...")
bot.polling(none_stop=True)
