import telebot
from flask import Flask, request
import re
import time
from collections import defaultdict
import os

TOKEN = "8253839434:AAGNEk7YPaehSuRz0FZ3U8_rLn7lg-9i-m4"
bot = telebot.TeleBot(TOKEN)

BAD_WORDS = [
    "нарк", "drug", "weed", "cocaine", "меф", "амф", "mdma",
    "порно", "sex", "porn", "xxx", "onlyfans",
    "казино", "casino", "bet", "betting", "gamble",
    "онлайн работа", "работа онлайн", "удаленно", "кол центр",
    "call center", "work online", "easy money",
    "бот", "spam", "реклама", "заработок","спам"
]

LINK_PATTERN = re.compile(r"http|www|t\.me|bit\.ly", re.IGNORECASE)
EMOJI_PATTERN = re.compile("[💊💉🌿🍑🍆💦🔞🎰💰🤑]", re.UNICODE)
user_messages = defaultdict(list)

app = Flask(__name__)

def ban_user(chat_id, user_id, message):
    try:
        bot.delete_message(chat_id, message.message_id)
        bot.ban_chat_member(chat_id, user_id)
    except Exception as e:
        print("Ban error:", e)

@bot.message_handler(func=lambda m: True)
def check_message(message):
    if not message.text:
        return

    text = message.text.lower()
    user_id = message.from_user.id
    chat_id = message.chat.id
    now = time.time()

    user_messages[user_id] = [t for t in user_messages[user_id] if now - t < 10]
    user_messages[user_id].append(now)

    if len(user_messages[user_id]) >= 5:
        ban_user(chat_id, user_id, message)
        return

    for word in BAD_WORDS:
        if word in text:
            ban_user(chat_id, user_id, message)
            return

    if LINK_PATTERN.search(text):
        ban_user(chat_id, user_id, message)
        return

    if EMOJI_PATTERN.search(text):
        ban_user(chat_id, user_id, message)
        return

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok"

@app.route("/")
def index():
    return "AntiSpam Bot is alive!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
