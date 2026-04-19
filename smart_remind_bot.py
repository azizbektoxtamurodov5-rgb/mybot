import telebot
from gtts import gTTS
import os
import time
import threading

TOKEN = '8559025596:AAGgec0hLbKuSU2tm47N01ue5b9Ka7A8mlQ'
CHANNEL_ID = '@pythoncommands'
bot = telebot.TeleBot(TOKEN)

def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status != 'left'
    except:
        return False

def send_reminder(chat_id, text, seconds):
    time.sleep(seconds)
    try:
        tts = gTTS(text=f"Eslatma: {text}", lang='tr')
        file_path = f"rem_{chat_id}.mp3"
        tts.save(file_path)
        with open(file_path, "rb") as audio:
            bot.send_voice(chat_id, audio, caption=f"🔔 Muhim ishingiz vaqti bo'ldi:\n\n📌 {text} 🚀")
        os.remove(file_path)
    except Exception:
        bot.send_message(chat_id, f"🔔 ✅ Muhim ishingiz vaqti bo'ldi: {text}")

@bot.message_handler(commands=['start'])
def start(message):
    if check_sub(message.from_user.id):
        welcome_text = (
            "👋 Assalomu alaykum! Men sizning shaxsiy yordamchingizman.\n\n"
            "Sizga muhim ishlaringizni vaqtida eslatib turaman! ✨\n\n"
            "📝 Namuna: \n5m Dars qilish yoki 10m Sayr qilish \n\n"
            "Men sizga bu muhim ishingizni ovozli xabar orqali eslataman! 🎙"
        )
        bot.send_message(message.chat.id, welcome_text)
    else:
        bot.send_message(message.chat.id, f"❌ Botdan foydalanish uchun kanalimizga a'zo bo'ling:\n\n👉 {CHANNEL_ID}\n\nA'zo bo'lgach, qayta /start bosing.")

@bot.message_handler(func=lambda message: True)
def set_reminder(message):
    if not check_sub(message.from_user.id):
        bot.send_message(message.chat.id, f"⚠️ Avval kanalga a'zo bo'ling: {CHANNEL_ID}")
        return

    try:
        parts = message.text.split(' ', 1)
        time_part = parts[0].lower()
        task_text = parts[1]
        
        if 'm' in time_part:
            minutes = int(time_part.replace('m', ''))
            seconds = minutes * 60
            bot.reply_to(message, f"✅ Kelishdik! {minutes} minutdan keyin sizga bu muhim ishingizni eslataman. ⏳")
            threading.Thread(target=send_reminder, args=(message.chat.id, task_text, seconds)).start()
    except:
        bot.reply_to(message, "❌ Xato! Namuna: 5m Dars qilish 📚")

if __name__ == "__main__":
    bot.infinity_polling()
