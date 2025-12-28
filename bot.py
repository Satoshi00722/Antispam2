import telebot
from flask import Flask, request
import re
import time
from collections import defaultdict
import os

TOKEN = "8253839434:AAGNEk7YPaehSuRz0FZ3U8_rLn7lg-9i-m4"
OWNER_ID = 7447763153  # <-- ТВОЙ ID

bot = telebot.TeleBot(TOKEN)

# Запрещенные слова, ссылки и эмодзи
BAD_WORDS = [
  "нарк", "drug", "weed", "cocaine", "меф", "амф", "mdma",
    "порно", "sex", "porn", "xxx", "onlyfans",
    "казино", "casino", "bet", "betting", "gamble",
    "онлайн работа", "работа онлайн", "удаленно", "кол центр",
    "call center", "work online", "easy money",
    "бот", "spam", "реклама", "заработок", "спам","weed","marijuana","cannabis","pot","ganja","herb","grass","bud","hash","hashish","hemp","kush","skunk",
    "dope","green","trees","smoke","blunt","joint","spliff","reefer","doobie","mj","mary jane","420","thc","cbd",
    "shatter","wax","oil","dab","rosin",
    "травка","марихуана","конопля","бошка","шишки","гандж","ганжа","план","гашиш","гаш","шмаль","дурь","зелень",
    "анаша","косяк","джойнт","блант","куш","скунс","мері джейн","тгк","кбд","масло","воск","даб",
    "tráva","marihuana","konopí","hasiš","haš","ganja","weed","skunk","kush","thc","cbd","olej","vosk",
    "pupeny","budky","joint","blunt",
    "weed","marihuana","cannabis","gras","kraut","ganja","hasch","haschisch","shit","dope","bubatz","grünes",
    "ott","piece","joint","blunt","tüte","spliff","thc","cbd","öl","wax","harz","kush","skunk",
    "трава","марихуана","конопля","шишки","бошка","ганжа","гандж","план","гашиш","гаш","шмаль","дурь","зелень",
    "анаша","косяк","кочка","джойнт","блант","куш","скунс","мэри джейн","тгк","кбд","масло","воск","даб","розин","coke","coca","cocaine","snow","blow","white","powder","line","rock","crack","freebase","amphetamine",
    "speed","meth","methamphetamine","crystal","ice","glass","shards","tina","crank","fast","pervitin","pep",
    "paste","bolivian","peruvian","yayo","nose candy","charlie",
    "кокс","кокаїн","сніг","білий","порошок","лінія","крек","кристал","мєт","метамфетамін","амфетамін",
    "фен","фенамін","швидкий","скід","скідуха","лід","скло","скотина","первітін","порох","паста","heroin","h","horse","smack","brown","black","tar","china white","gear","junk","opium","morphine",
    "morph","oxy","oxycodone","oxys","fentanyl","fent","patch","codeine","lean","purple drank","sizzurp",
    "tramadol","tramal",
    "героїн","герыч","гера","гарик","кінь","конина","коричневий","чорний","мак","опій","морфій","оксі",
    "оксиконтин","фентаніл","кодеїн","лін","пурпурний п'ян","lsd","acid","tabs","blotter","trips","microdots","dots","lucy","mushrooms","shrooms","magic mushrooms",
    "psilocybin","boomers","dmt","dimitri","spirit molecule","2c-b","nexus","2c-i","mescaline","cactus",
    "peyote","ketamine","k","special k","kitty","vitamin k","pcp","angel dust","salvia",
    "лсд","кислота","марка","марки","папер","трип","мікродоти","гриби","грибочки","псилоцибін","дмт",
    "кетамін","кета","кечка","спешл кей","феніциклід","пцп","сальвія","mdma","ecstasy","xtc","e","x","molly","pills","rolls","beans","mandy","candy","love drug","methylone",
    "mephedrone","meow meow","4-mmc","bath salts","synthetic cathinones","spice","k2","jwh","synthetic cannabinoids","noids",
    "мдма","екстазі","моллі","таблетки","качі","пігулки","менді","цукерки","мефедрон","мяу-мяу","4-ммц","соль",
    "бат салтс","спайс","синтетика","джей-дабл-ю-ейч","синтетичні канабіноїди","xanax","alprazolam","benzodiazepines","benzos","bars","zannies","valium","diazepam","ativan","klonopin","rohypnol",
    "roofies","ghb","liquid ecstasy","poppers","amyl nitrite","laughing gas","nitrous oxide","nangs","whippets","dxm",
    "dextromethorphan","lean","promethazine","sprite","jolly rancher",
    "ксанакс","алпразолам","бензодіазепіни","бензи","плитки","валіум","діазепам","рогіпнол","ггб","рідке екстазі",
    "попперс","веселячий газ","закис азоту","дхм","декстрометорфан","buy","sell","deal","dealer","vendor","plug","connect","supplier","source","steerer","middleman","trapper","hustler",
    "score","cop","pick up","re-up","stock","onion","dnm",
    "high","stoned","baked","fried","wasted","gone","blasted","ripped","smacked","tripping","rolling","peaking",
    "coming up","buzz","rush","nod","nodding off","euphoria","binge","chasing the dragon","bag","sack","g","gram","ounce","oz","pound","lb","kilo","key","brick","piece","dose","hit","stamp","ball","8-ball",
    "wrap","parachute","baggie","scale","weight","pipe","bong","bubblier","vape","dab rig","needle","spike","syringe","point",
    "foil","tinfoil","mirror","plate","straw","roll","grinder","crusher","roach","filter",
    "check my profile","link in bio","telegram: @","wickr","signal","session","email for info","pm for details","dm me",
    "contact for menu","menu available","fast delivery","24/7","reliable","trusted","no bs","no scam","verified",
    "профіль","ссилка в біо","телеграм канал","вікр","сігнал","напишіть в особисті","меню в профілі","швидка доставка",
    "цілодобово","надійно","без шахрайства","стелс упаковка","безпечно","дискретно","найкращі ціни","якість","чистий",
     "міцний", "для вечірок", "товар", "речі", "цукерки",
    "піца", "кава", "іграшки", "їжа", "оплата",

    "$", "₽", "€", "₴", "р", "p",

    # добавленные слова
    "собрать",
    "предоставлю",
    "темка",
    "забираешь",
    "рублей",
    "выплата"
]

LINK_PATTERN = re.compile(r"http|www|t\.me|bit\.ly", re.IGNORECASE)
EMOJI_PATTERN = re.compile("[💊💉🌿🍑🍆💦🔞🎰💰🤑]", re.UNICODE)

# Хранение сообщений для антифлуда
user_messages = defaultdict(lambda: defaultdict(list))

app = Flask(__name__)

# ---------- ПРОВЕРКА АДМИНА / ВЛАДЕЛЬЦА ----------
def is_admin_or_owner(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False

def ban_user(chat_id, user_id, message, reason="Спам/реклама"):
    try:
        bot.delete_message(chat_id, message.message_id)

        bot.restrict_chat_member(
            chat_id,
            user_id,
            until_date=int(time.time()) + 604800,
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False
        )

        text = f"""
<b>⚠️ Внимание!</b>

Пользователь: <b>@{message.from_user.username or message.from_user.first_name}</b>
<b>заблокирован на 7 дней.</b>

Для уточнения пришлите ваше обращение администратору для одобрения: <b>@SUPEVSE</b>
"""
        bot.send_message(chat_id, text, parse_mode="HTML")
    except Exception as e:
        print("Ban error:", e)

# ---------- ОСНОВНАЯ ПРОВЕРКА СООБЩЕНИЙ ----------
@bot.message_handler(func=lambda m: True)
def check_message(message):
    chat_id = message.chat.id

    # 🔥 АНОНИМНЫЙ АДМИН ИЛИ СООБЩЕНИЕ ОТ КАНАЛА — ПОЛНЫЙ ИГНОР
    if message.sender_chat is not None:
        return

    user_id = message.from_user.id

    # 🔥 ОБЫЧНЫЙ АДМИН И ВЛАДЕЛЕЦ — ПОЛНЫЙ ИГНОР
    if is_admin_or_owner(chat_id, user_id):
        return

    if not message.text:
        return

    text = message.text.lower()
    now = time.time()

    # АНТИФЛУД
    user_messages[chat_id][user_id] = [
        t for t in user_messages[chat_id][user_id] if now - t < 10
    ]
    user_messages[chat_id][user_id].append(now)

    if len(user_messages[chat_id][user_id]) >= 5:
        ban_user(chat_id, user_id, message, "Флуд")
        return

    # Запрещенные слова
    for word in BAD_WORDS:
        if word in text:
            ban_user(chat_id, user_id, message, f"Запрещенное слово: {word}")
            return

    # Ссылки
    if LINK_PATTERN.search(text):
        ban_user(chat_id, user_id, message, "Ссылка/реклама")
        return

    # Эмодзи
    if EMOJI_PATTERN.search(text):
        ban_user(chat_id, user_id, message, "Спам эмодзи")
        return

# ---------- WEBHOOK ----------
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
