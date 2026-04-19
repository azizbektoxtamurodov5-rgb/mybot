import telebot
from telebot import types
from gtts import gTTS
import os
import time
import threading
import requests
import schedule
from datetime import datetime
import pytz

# SOZLAMALAR
TOKEN = '8559025596:AAF3TDGjtun1LYvSa9_h6nu3lFiVykAxLWw'
WEATHER_API = 'cfb18895da0d8bf04a8307cc8550fe0d'
CHANNEL_ID = '@pythoncommands'
CITY = 'Zaamin' # Zomin shahri uchun

bot = telebot.TeleBot(TOKEN)

# OB-HAVO FUNKSIYASI (Zomin uchun)
def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API}&units=metric&lang=uz"
    try:
        res = requests.get(url).json()
        temp = res['main']['temp']
        status = res['weather'][0]['description']
        humidity = res['main']['humidity']
        text = (f"🌤 **Zomin ob-havosi:**\n\n"
                f"🌡 Harorat: {temp}°C\n"
                f"☁️ Holat: {status.capitalize()}\n"
                f"💧 Namlik: {humidity}%\n"
                f"🕒 Vaqt: {datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%H:%M')}")
        return text
    except:
        return "❌ Zomin ob-havosini olib bo'lmadi."

# KANALGA AVTOMATIK YUBORISH
def auto_weather():
    weather_text = get_weather()
    try:
        bot.send_message(CHANNEL_ID, f"📢 **KUNLIK OB-HAVO (Zomin)**\n\n{weather_text}", parse_mode='Markdown')
    except:
        pass

# VAQT REJASI
def run_schedule():
    schedule.every().day.at("08:00").do(auto_weather)
    schedule.every().day.at("20:00").do(auto_weather)
    while True:
        schedule.run_pending()
        time.sleep(60)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("🌤 Ob-havoni ko'rish")
    markup.add(btn)
    bot.send_message(message.chat.id, "👋 Salom! Bot Zomin ob-havosiga sozlandi.\n\nEslatma uchun: '5m Dars' deb yozing.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🌤 Ob-havoni ko'rish")
def send_weather(message):
    bot.send_message(message.chat.id, get_weather(), parse_mode='Markdown')

def send_reminder(chat_id, text, seconds):
    time.sleep(seconds)
    try:
        tts = gTTS(text=f"Eslatma: {text}", lang='tr')
        file_path = f"rem_{chat_id}.mp3"
        tts.save(file_path)
        with open(file_path, "rb") as audio:
            bot.send_voice(chat_id, audio, caption=f"🔔 Vaqti bo'ldi: {text}")
        os.remove(file_path)
    except:
        bot.send_message(chat_id, f"🔔 Vaqti bo'ldi: {text}")

@bot.message_handler(func=lambda message: 'm ' in message.text.lower())
def set_reminder(message):
    try:
        parts = message.text.split(' ', 1)
        minutes = int(parts[0].replace('m', ''))
        task = parts[1]
        bot.reply_to(message, f"✅ {minutes} minutga o'rnatildi!")
        threading.Thread(target=send_reminder, args=(message.chat.id, task, minutes*60)).start()
    except:
        pass

if __name__ == "__main__":
    threading.Thread(target=run_schedule, daemon=True).start()
    bot.infinity_polling()
