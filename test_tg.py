import os
from io import BytesIO
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError
from PIL import Image, ImageDraw
import asyncio

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def create_dummy_screenshot():
    img = Image.new("RGB", (200, 100), color="white")
    d = ImageDraw.Draw(img)
    d.text((10, 40), "Test Screenshot", fill="black")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()

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

async def main():
    dummy_screenshot = create_dummy_screenshot()
    dummy_analysis = {
        "trend": "Bullish",
        "signal": "BUY",
        "price": 123.45,
        "rsi": 55.5,
        "ema_50": 120.0,
        "ema_200": 110.0,
        "sl": 118.0,
        "tp": 130.0,
        "rr": 2.5,
        "pivots": {
            "pivot": 121.0,
            "support1": 115.0,
            "resistance1": 125.0
        },
        "candle_pattern": "Engulfing"
    }
    await send_telegram_signal("TESTPAIR", dummy_analysis, dummy_screenshot)

if __name__ == "__main__":
    asyncio.run(main())
