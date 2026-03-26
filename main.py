import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import time

# ---------------- CONFIG ----------------
BOT_TOKEN = "8604072281:AAGvz-xBuV9_Fljc2ceD7GbfoP0tHXx0Zvo"
API_URL = "http://147.135.212.197/crapi/st/viewstats"
API_TOKEN = "RFdUREJBUzR9T4dVc49ndmFra1NYV5CIhpGVcnaOYmqHhJZXfYGJSQ=="

CHANNELS = [
    "@ProTech43",
    "@HematTech",
    "@SQ_BOTZ",
    "@SQ_ZONE",
    "@HEMATOTP"
]

# ---------------- STORAGE ----------------
users = {}
referrals = {}
sent_numbers = set()

# ---------------- JOIN CHECK ----------------
def is_joined(bot, user_id):
    for ch in CHANNELS:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# ---------------- START ----------------
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    # referral
    if context.args:
        ref = int(context.args[0])
        if ref != user_id:
            referrals.setdefault(ref, []).append(user_id)

    users[user_id] = True

    keyboard = []
    for ch in CHANNELS:
        keyboard.append([InlineKeyboardButton(ch, url=f"https://t.me/{ch[1:]}")])

    keyboard.append([InlineKeyboardButton("✅ Check Join", callback_data="check")])

    update.message.reply_text(
        "🔒 لطفآ لاندې چینلونو کې ګډون وکړئ:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- CHECK JOIN ----------------
def check_join(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    if is_joined(context.bot, user_id):
        keyboard = [
            [InlineKeyboardButton("📊 زما حساب", callback_data="panel")]
        ]
        query.edit_message_text(
            "✅ تاسو ټول چینلونو کې شامل یاست!\n\n🎉 مینو ته ښه راغلاست:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        query.answer("❌ مهرباني وکړئ ټول چینلونو کې ګډون وکړئ!", show_alert=True)

# ---------------- PANEL ----------------
def panel(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    count = len(referrals.get(user_id, []))
    link = f"https://t.me/{context.bot.username}?start={user_id}"

    text = f"""
👤 *ستاسو حساب*

👥 ریفیرل: {count}/10

🔗 ستاسو لینک:
{link}
"""

    query.edit_message_text(text, parse_mode="Markdown")

# ---------------- FETCH NUMBERS ----------------
def fetch_numbers():
    try:
        r = requests.get(API_URL, params={"token": API_TOKEN}, timeout=20)
        data = r.json()
        return data if isinstance(data, list) else []
    except:
        return []

# ---------------- SEND NUMBERS ----------------
def send_numbers(context: CallbackContext):
    data = fetch_numbers()

    for item in data:
        try:
            phone = item[1]
            time_str = item[3]

            if phone in sent_numbers:
                continue

            sent_numbers.add(phone)

            for user_id in users:
                count = len(referrals.get(user_id, []))

                if count < 10:
                    context.bot.send_message(
                        chat_id=user_id,
                        text="❗ لطفآ 10 ملګري دعوت کړئ تر څو نمبر ترلاسه کړئ."
                    )
                    continue

                text = f"""📢 *نوی نمبر جوړ شو*

> 📞 نمبر: `{phone}`
> ⏰ وخت: {time_str}

━━━━━━━━━━━━"""

                keyboard = [[
                    InlineKeyboardButton("🔑 کوډ یی دلته پیدا کړی", url="https://t.me/HematOTP")
                ]]

                context.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

        except:
            continue

# ---------------- MAIN ----------------
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(check_join, pattern="check"))
    dp.add_handler(CallbackQueryHandler(panel, pattern="panel"))

    updater.job_queue.run_repeating(send_numbers, interval=30, first=10)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
