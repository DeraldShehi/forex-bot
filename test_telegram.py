import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("ERROR: TELEGRAM_TOKEN ose TELEGRAM_CHAT_ID nuk janë vendosur në .env")
    exit(1)

bot = Bot(token=TELEGRAM_TOKEN)

async def main():
    print("Duke dërguar mesazhin në Telegram...")
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Test i thjeshtë nga bot - funksionon!")
        print("Mesazhi u dërgua me sukses!")
    except Exception as e:
        print("Gabim gjatë dërgimit të mesazhit:", e)

if __name__ == "__main__":
    asyncio.run(main())
