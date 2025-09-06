import telebot
from telebot import types
from datetime import datetime
import os

# استدعاء التوكن من متغيرات البيئة
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = telebot.TeleBot(BOT_TOKEN)

# قاعدة بيانات مبسطة (في الذاكرة)
users = {}

def check_user(chat_id):
    today = datetime.now().strftime("%Y-%m-%d")
    if chat_id not in users:
        users[chat_id] = {"premium": False, "count": 0, "last_day": today}
    if users[chat_id]["last_day"] != today:
        users[chat_id]["count"] = 0
        users[chat_id]["last_day"] = today
    return users[chat_id]

@bot.message_handler(commands=['start'])
def start(message):
    user = check_user(message.chat.id)
    bot.reply_to(message, "👋 أهلا بك! أرسل لي ملف PDF وسأحوّله لك إلى Word.\n\n"
                          "المستخدم المجاني: 5 عمليات يومياً.\n"
                          "المستخدم البريميوم: غير محدود.")

@bot.message_handler(content_types=['document'])
def handle_file(message):
    user = check_user(message.chat.id)

    # تحقق من الحد
    if not user["premium"] and user["count"] >= 5:
        bot.reply_to(message, "❌ وصلت للحد اليومي (5 ملفات).\n💎 اشترك في البريميوم لمزيد من العمليات.")
        return

    # هنا مكان التحويل (تقدر تضيف دوال PDF → Word أو صيغ أخرى)
    bot.reply_to(message, f"📂 استلمت ملف: {message.document.file_name}\n(هنا هيتم التحويل...)")

    user["count"] += 1

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.chat.id != ADMIN_ID:
        return
    total_users = len(users)
    premium_users = sum(1 for u in users.values() if u["premium"])
    bot.reply_to(message, f"📊 إحصائيات:\n"
                          f"👥 إجمالي المستخدمين: {total_users}\n"
                          f"💎 مستخدمين بريميوم: {premium_users}")

print("✅ البوت يعمل على Render...")
bot.polling(none_stop=True)
