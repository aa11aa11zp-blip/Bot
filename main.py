import requests
import time
from telegram import Bot

# ------------ CONFIG ------------
API_URL = "http://147.135.212.197/crapi/st/viewstats"
API_TOKEN = "RFdUREJBUzR9T4dVc49ndmFra1NYV5CIhpGVcnaOYmqHhJZXfYGJSQ=="

BOT_TOKEN = "8281944831:AAGrz2zrLVLwdDd2BKISYUndRnD6yLn8pEE"
CHAT_ID = -1003819384817

bot = Bot(token=BOT_TOKEN)

# د duplicate مخنیوی
sent_numbers = set()

print("🚀 BOT STARTED...")

def fetch_data():
    try:
        res = requests.get(API_URL, params={"token": API_TOKEN}, timeout=20)
        res.raise_for_status()
        data = res.json()

        # debug
        print("API:", data[:1] if isinstance(data, list) else data)

        return data if isinstance(data, list) else []
    except Exception as e:
        print("❌ API ERROR:", e)
        return []

while True:
    data = fetch_data()

    for item in data:
        try:
            # flexible read
            if isinstance(item, list) and len(item) >= 2:
                phone = item[1]
            elif isinstance(item, dict):
                phone = item.get("phone") or item.get("number")
            else:
                continue

            if not phone:
                continue

            # duplicate skip
            if phone in sent_numbers:
                continue

            sent_numbers.add(phone)

            # send only number
            text = f"📱 New Number:\n{phone}"

            bot.send_message(chat_id=CHAT_ID, text=text)

            print("✅ SENT:", phone)

        except Exception as e:
            print("❌ ERROR:", e)

    time.sleep(20) 
