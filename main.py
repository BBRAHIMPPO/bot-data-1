import threading
import time
import random
import os
import telebot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# --- الإعدادات ---
TOKEN = "8678424700:AAFSt9OSJCvz9kFGJBxskW74a-euN4Oe994"
bot = telebot.TeleBot(TOKEN)

is_running = False
seen_links = set()

def get_driver():
    """إعداد احترافي لـ Render لضمان اشتغال الكروم"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # تحديد مسار الكروم في Render (هذا هو السر)
    chrome_bin = os.environ.get("GOOGLE_CHROME_BIN")
    if chrome_bin:
        chrome_options.binary_location = chrome_bin

    # إخفاء هوية البوت
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # محاولة تشغيل Driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def scrape_logic(chat_id):
    global is_running
    driver = None
    keywords = ["correct score", "fixed match", "1-0 full time"]

    while is_running:
        try:
            bot.send_message(chat_id, "🔍 جاري فتح المتصفح والبحث...")
            if not driver:
                driver = get_driver()
            
            for word in keywords:
                if not is_running: break
                
                driver.get(f"https://www.threads.net/search?q={word}")
                time.sleep(random.uniform(7, 12)) 

                # سكرول خفيف
                body = driver.find_element(By.TAG_NAME, 'body')
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(3)

                profiles = driver.find_elements(By.XPATH, "//a[contains(@href, '/@')]")
                profile_urls = list(set([p.get_attribute('href') for p in profiles]))[:10] # ليميت لـ 10 بروفايلات في الدورة

                for profile in profile_urls:
                    if not is_running: break
                    try:
                        driver.get(profile)
                        time.sleep(random.uniform(5, 8))
                        
                        links = driver.find_elements(By.TAG_NAME, 'a')
                        for l in links:
                            href = l.get_attribute('href')
                            if href and ('t.me/' in href or 'telegram.me' in href):
                                if href not in seen_links:
                                    bot.send_message(chat_id, f"🎯 صيد جديد:\n🔗 {href}")
                                    seen_links.add(href)
                    except:
                        continue
            
            bot.send_message(chat_id, "😴 دورة انتهت، استراحة 5 دقائق...")
            time.sleep(300) 

        except Exception as e:
            bot.send_message(chat_id, f"⚠️ خطأ تقني: {str(e)[:100]}")
            if driver: driver.quit()
            driver = None
            time.sleep(20)

@bot.message_handler(func=lambda m: m.text == "999")
def start_bot(message):
    global is_running
    if not is_running:
        is_running = True
        bot.reply_to(message, "🚀 السكريبت انطلق فعلياً!")
        threading.Thread(target=scrape_logic, args=(message.chat.id,)).start()

@bot.message_handler(func=lambda m: m.text == "000")
def stop_bot(message):
    global is_running
    is_running = False
    bot.reply_to(message, "🛑 توقف.")

bot.polling(none_stop=True)
