import telebot
from flask import Flask, request
import re
import time
from collections import defaultdict
import os

TOKEN = "8253839434:AAGNEk7YPaehSuRz0FZ3U8_rLn7lg-9i-m4"
bot = telebot.TeleBot(TOKEN)

# ID владельца бота (только он может активировать)
OWNER_ID = 7447763153

# Запрещенные слова, ссылки и эмодзи
BAD_WORDS = [
    "нарк", "drug", "weed", "cocaine", "меф", "амф", "mdma",
    "порно", "sex", "porn", "xxx", "onlyfans",
    "казино", "casino", "bet", "betting", "gamble",
    "онлайн работа", "работа онлайн", "удаленно", "кол центр",
    "call center", "work online", "easy money",
    "бот", "spam", "реклама", "заработок", "спам"
]

LINK_PATTERN = re.compile(r"http|www|t\.me|bit\.ly", re.IGNORECASE)
EMOJI_PATTERN = re.compile("[💊💉🌿🍑🍆💦🔞🎰💰🤑]", re.UNICODE)

# Хранение сообщений для антифлуда
user_messages = defaultdict(lambda: defaultdict(list))  # {chat_id: {user_id: [timestamps]}}

# Список авторизованных чатов
AUTHORIZED_CHATS = set()

app = Flask(__name__)

def ban_user(chat_id, user_id, message, reason="Спам/реклама"):
    """Удаляет сообщение, мутит пользователя и отправляет уведомление в чат"""
    try:
        # Удаляем сообщение
        bot.delete_message(chat_id, message.message_id)
        
        # Ограничение пользователя на 7 дней
        bot.restrict_chat_member(
            chat_id,
            user_id,
            until_date=int(time.time()) + 604800,
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False
        )
        
        # Красивое уведомление
        text = f"""
<b>⚠️ Внимание!</b>

Пользователь: <b>@{message.from_user.username or message.from_user.first_name}</b>
<b>заблокирован на 7 дней.</b>

Причина: <i>{reason}</i>

Для уточнения пришлите ваше обращение администратору для одобрения: <b>@SUPEVSE</b>
"""
        bot.send_message(chat_id, text, parse_mode="HTML")
    except Exception as e:
        print("Ban error:", e)

# Команда /start — активирует бота только владельцем
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id != OWNER_ID:
        bot.send_message(chat_id, "❌ Этот бот может быть активирован только доверенным администратором.")
        bot.leave_chat(chat_id)  # выходим из группы
        return

    AUTHORIZED_CHATS.add(chat_id)
    bot.send_message(chat_id, "✅ Бот активирован в этом чате!")

# Основная проверка сообщений
@bot.message_handler(func=lambda m: True)
def check_message(message):
    chat_id = message.chat.id

    # Игнорируем все чаты, где бот не был активирован владельцем
    if chat_id not in AUTHORIZED_CHATS:
        return

    if not message.text:
        return

    text = message.text.lower()
    user_id = message.from_user.id
    now = time.time()

    # АНТИФЛУД: не более 5 сообщений за 10 секунд
    user_messages[chat_id][user_id] = [
        t for t in user_messages[chat_id][user_id] if now - t < 10
    ]
    user_messages[chat_id][user_id].append(now)

    if len(user_messages[chat_id][user_id]) >= 5:
        ban_user(chat_id, user_id, message, reason="Флуд")
        return

    # Проверка на запрещенные слова
    for word in BAD_WORDS:
        if word in text:
            ban_user(chat_id, user_id, message, reason=f"Запрещенное слово: {word}")
            return

    # Проверка на ссылки
    if LINK_PATTERN.search(text):
        ban_user(chat_id, user_id, message, reason="Ссылка/реклама")
        return

    # Проверка на эмодзи
    if EMOJI_PATTERN.search(text):
        ban_user(chat_id, user_id, message, reason="Спам эмодзи")
        return

# Вебхук для Telegram
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


