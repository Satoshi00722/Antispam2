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

# ================== ЗАПРЕЩЕННЫЕ СЛОВА ==================
BAD_WORDS = [
    # 🔞 ПОРНО / СЕКС
    "порно","porn","sex","xxx","onlyfans","escort","эскорт",
    "проститутка","проституция","шлюха","девочки","массаж",
    "cam","webcam","cams","nude","nudes","nsfw",
    "hooker","brothel","strip","striptease",
    "интим","интим услуги","sex service","vip girls",

    # 💊 НАРКОТИКИ
    "нарк","drug","drugs","weed","marijuana","cannabis","ganja","hash","hashish","hemp",
    "kush","skunk","dope","420","thc","cbd",
    "cocaine","coke","snow","crack","amphetamine","speed","meth","ice",
    "mdma","ecstasy","xtc","molly","mephedrone","4-mmc",
    "heroin","opium","morphine","fentanyl","tramadol",
    "lsd","acid","dmt","ketamine","shrooms","psilocybin",
    "spice","k2","noids",
    "трава","марихуана","конопля","шишки","бошка","ганжа","гандж",
    "меф","амф","фен","героин","гашиш","анаша","косяк",

    # 💃 ПРОСТИТУЦИЯ / ЭСКОРТ
    "индивидуалка","escort service","эскорт услуги",

    # 💱 ОБМЕННИКИ / КРИПТА
    "обмен","обменник","exchange","crypto exchange",
    "usdt","btc","bitcoin","ethereum",
    "нал","кеш","cash","без верификации","no kyc",
    "быстрый обмен","анонимно",

    # 🎭 МОШЕННИКИ
    "скам","scam","мошенник","мошенники","fraud",
    "развод","обман","кидалово","фейк",
    "гарант","без риска","100%","проверенный",
    "no scam","trusted","verified","fast profit",

    # 💸 БЫСТРЫЕ ДЕНЬГИ
    "быстрые деньги","easy money","лёгкий заработок",
    "заработок без вложений","работа онлайн",
    "удаленно","call center","кол центр",
    "инвестиции 100%","пассивный доход",
    "деньги за день","профит","income",
    "оплата","+420","+380","+7",

    "$", "₽", "€", "₴", "р", "p",

    # добавленные
    "собрать","предоставлю","темка",
    "забираешь","рублей","выплата"
]

LINK_PATTERN = re.compile(r"http|www|t\.me|bit\.ly", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"\+?\d[\d\s\-]{7,}")
EMOJI_PATTERN = re.compile("[💊💉🌿🍑🍆💦🔞🎰💰🤑]", re.UNICODE)

user_messages = defaultdict(lambda: defaultdict(list))

app = Flask(__name__)

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
def warn_user(chat_id, message, reason):
    try:
        bot.delete_message(chat_id, message.message_id)

        text = """
🤖 <b>Хотите разместить объявление без риска блокировки?</b>

✅ Используйте официальный автоматизированный бот публикации:
• проверка контента
• безопасная публикация
• без общения с администрацией

👉 <b>Перейти в бот для размещения:</b>
@CleanModerChat_bot
"""

        sent = bot.send_message(chat_id, text, parse_mode="HTML")
        delete_later(chat_id, sent.message_id, 300)

    except Exception as e:
        print("Warn error:", e)

# ================== ПРОВЕРКА СООБЩЕНИЙ ==================
@bot.message_handler(func=lambda m: True, content_types=[
    "text", "photo", "video", "animation", "sticker", "document"
])
def check_message(message):
    chat_id = message.chat.id

    if message.sender_chat:
        return

    user_id = message.from_user.id

    if is_admin(chat_id, user_id):
        return

    now = time.time()
    text = (message.text or "").lower()

    # ❌ ПЕРЕСЛАННЫЕ СООБЩЕНИЯ
    if message.forward_from or message.forward_from_chat or message.forward_sender_name:
        warn_user(chat_id, message, "Пересланные сообщения запрещены")
        return

    # АНТИФЛУД
    user_messages[chat_id][user_id] = [
        t for t in user_messages[chat_id][user_id] if now - t < 10
    ]
    user_messages[chat_id][user_id].append(now)

    if len(user_messages[chat_id][user_id]) >= 5:
        warn_user(chat_id, message, "Флуд")
        return

    # ❌ ТЕЛЕФОНЫ
    if PHONE_PATTERN.search(text):
        warn_user(chat_id, message, "Контактные данные")
        return

    # ❌ ЗАПРЕЩЕННЫЕ СЛОВА
    for word in BAD_WORDS:
        if word in text:
            warn_user(chat_id, message, "Запрещённый контент")
            return

    # ❌ ССЫЛКИ
    if LINK_PATTERN.search(text):
        warn_user(chat_id, message, "Ссылки запрещены")
        return

    # ❌ ЭМОДЗИ
    if EMOJI_PATTERN.search(text):
        warn_user(chat_id, message, "Спам-эмодзи")
        return

# ================== WEBHOOK ==================
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


