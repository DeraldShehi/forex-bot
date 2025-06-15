from telegram import Bot
from telegram.error import TelegramError
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def send_telegram_signal(pair, analysis, screenshot_bytes):
    message = (
        f"📊 Sinjal për {pair}\n"
        f"Trend: {analysis['trend']}\n"
        f"Sinjal: {analysis['signal']}\n"
        f"Çmimi: {analysis['price']:.2f}\n"
        f"RSI: {analysis['rsi']:.2f}\n"
        f"EMA50: {analysis['ema_50']:.2f}\n"
        f"EMA200: {analysis['ema_200']:.2f}\n"
        f"SL: {analysis['sl']:.2f}\n"
        f"TP: {analysis['tp']:.2f}\n"
        f"Risk/Reward: {analysis['rr']:.2f}\n"
        f"Pivot: {analysis['pivots']['pivot']:.2f}\n"
        f"Support1: {analysis['pivots']['support1']:.2f}\n"
        f"Resistance1: {analysis['pivots']['resistance1']:.2f}\n"
        f"Candle pattern: {analysis['candle_pattern'] or 'Nuk u gjet'}"
    )
    try:
        await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=BytesIO(screenshot_bytes), caption=message)
        print(f"✅ Sinjali u dërgua për {pair}")
    except TelegramError as e:
        print(f"❌ Gabim gjatë dërgimit: {e}")
