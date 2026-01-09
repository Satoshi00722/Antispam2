import telebot
from flask import Flask, request
import re
import time
from collections import defaultdict
import os
import threading

TOKEN = "8253839434:AAGNEk7YPaehSuRz0FZ3U8_rLn7lg-9i-m4"
OWNER_ID = 7447763153

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ================== ЗАПРЕЩЕННЫЕ СЛОВА ==================
BAD_WORDS = [
    "порно","porn","sex","xxx","onlyfans","escort","эскорт",
    "проститутка","проституция","шлюха","девочки","массаж",
    "cam","webcam","cams","nude","nudes","nsfw",
    "hooker","brothel","strip","striptease",
    "интим","интим услуги","sex service","vip girls",

    "нарк","drug","drugs","weed","marijuana","cannabis","ganja","hash","hashish","hemp",
    "kush","skunk","dope","420","thc","cbd",
    "cocaine","coke","snow","crack","amphetamine","speed","meth","ice",
    "mdma","ecstasy","xtc","molly","mephedrone","4-mmc",
    "heroin","opium","morphine","fentanyl","tramadol",
    "lsd","acid","dmt","ketamine","shrooms","psilocybin",
    "spice","k2","noids",

    "трава","марихуана","конопля","шишки","бошка","ганжа","гандж",
    "меф","амф","фен","героин","гашиш","анаша","косяк",

    "индивидуалка","escort service","эскорт услуги",

    "обмен","обменник","exchange","crypto exchange",
    "usdt","btc","bitcoin","ethereum",
    "нал","кеш","cash","без верификации","no kyc",
    "быстрый обмен","анонимно",

    "скам","scam","мошенник","мошенники","fraud",
    "развод","обман","кидалово","фейк",
    "гарант","без риска","100%","проверенный",
    "no scam","trusted","verified","fast profit",

    "быстрые деньги","easy money","лёгкий заработок",
    "заработок без вложений","работа онлайн",
    "удаленно","call center","кол центр",
    "инвестиции 100%","пассивный доход",
    "деньги за день","профит","income",
    "оплата","+420","+380","+7",

    "$", "₽", "€", "₴", "р", "p",

    "собрать","предоставлю","темка",
    "забираешь","рублей","выплата"
]

LINK_PATTERN = re.compile(r"http|www|t\.me|bit\.ly", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"\+?\d[\d\s\-]{7,}")
EMOJI_PATTERN = re.compile("[💊💉🌿🍑🍆💦🔞🎰💰🤑]", re.UNICODE)

user_messages = defaultdict(lambda: defaultdict(list))

# ================== УДАЛЕНИЕ С ЗАДЕРЖКОЙ ==================
def delete_later(chat_id, message_id, delay=300):
    def worker():
        time.sleep(delay)
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
    threading.Thread(target=worker, daemon=True).start()

# ================== ПРОВЕРКА АДМИНА ==================
def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False

# ================== ПРЕДУПРЕЖДЕНИЕ ==================
def warn_user(chat_id, message):
    try:
        bot.delete_message(chat_id, message.message_id)

       text = (
    "🤖 <b>Хотите разместить объявление без риска блокировки?</b>\n\n"
    "✅ Используйте официальный автоматизированный бот публикации:\n"
    "• проверка контента\n"
    "• безопасная публикация\n"
    "• без общения с администрацией\n\n"
    "👉 <b>Перейти в бот для размещения:</b>\n"
    "@CleanModerChat_bot"
)

        sent = bot.send_message(chat_id, text, parse_mode="HTML")
        delete_later(chat_id, sent.message_id, 300)
    except:
        pass

# ================== ПРОВЕРКА СООБЩЕНИЙ ==================
@bot.message_handler(
    func=lambda m: True,
    content_types=[
        "text","photo","video","animation","sticker",
        "document","voice","video_note","audio"
    ]
)
def check_message(message):
    chat_id = message.chat.id

    # 🟢 1. ПРОПУСКАЕМ КАНАЛ И АНОНИМНЫХ АДМИНОВ
    if message.sender_chat:
        return

    # 🟢 2. ПРОПУСКАЕМ АДМИНОВ
    if message.from_user and is_admin(chat_id, message.from_user.id):
        return

    # ❌ 3. ПЕРЕСЛАННЫЕ СООБЩЕНИЯ
    if (
        message.forward_from
        or message.forward_from_chat
        or message.forward_sender_name
        or message.forward_date
    ):
        warn_user(chat_id, message)
        return

    # ❌ 4. ЛЮБОЙ МЕДИА-КОНТЕНТ
    if (
        message.photo or message.video or message.animation or
        message.sticker or message.document or message.voice or
        message.video_note or message.audio
    ):
        warn_user(chat_id, message)
        return

    # ================== АНТИФЛУД ==================
    now = time.time()
    user_id = message.from_user.id

    user_messages[chat_id][user_id] = [
        t for t in user_messages[chat_id][user_id] if now - t < 10
    ]
    user_messages[chat_id][user_id].append(now)

    if len(user_messages[chat_id][user_id]) >= 5:
        warn_user(chat_id, message)
        return

    text = (message.text or "").lower()

    # ❌ ТЕЛЕФОНЫ
    if PHONE_PATTERN.search(text):
        warn_user(chat_id, message)
        return

    # ❌ ССЫЛКИ
    if LINK_PATTERN.search(text):
        warn_user(chat_id, message)
        return

    # ❌ ЭМОДЗИ
    if EMOJI_PATTERN.search(text):
        warn_user(chat_id, message)
        return

    # ❌ ЗАПРЕЩЕННЫЕ СЛОВА
    for word in BAD_WORDS:
        if word in text:
            warn_user(chat_id, message)
            return

# ================== WEBHOOK ==================
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(
        request.get_data().decode("utf-8")
    )
    bot.process_new_updates([update])
    return "ok"

@app.route("/")
def index():
    return "AntiSpam Bot is alive!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
