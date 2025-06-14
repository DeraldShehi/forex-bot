import asyncio
from telegram import Bot

TELEGRAM_TOKEN = "7282786151:AAGsxS0wVv_YTPpO8OeRAVozYU3uh-adOZM"
TELEGRAM_CHAT_ID = 882227189

async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="✅ Boti i Forex është gati për aksion!")

if __name__ == "__main__":
    asyncio.run(main())
