import os
import asyncio
import datetime
import aiohttp
import pandas as pd
import talib as ta
from io import BytesIO
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError
from pyppeteer import launch

load_dotenv()

ALPHA_API_KEY = os.getenv("ALPHA_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not ALPHA_API_KEY or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise Exception("Vendosni të gjitha çelësat në .env: ALPHA_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

PAIRS = ["AUDCAD", "EURUSD", "XAUUSD", "BTCUSD"]

def eshte_fundjave(pair):
    now = datetime.datetime.utcnow()
    weekday = now.weekday()  # 0=Monday, 6=Sunday
    if pair == "BTCUSD":
        return False  # Crypto 24/7
    return weekday >= 5  # Saturday=5, Sunday=6

async def get_data(symbol, interval="DAILY"):
    base_url = "https://www.alphavantage.co/query"
    params = {}

    if symbol == "BTCUSD":
        # Crypto daily
        function = "DIGITAL_CURRENCY_DAILY"
        params = {
            "function": function,
            "symbol": "BTC",
            "market": "USD",
            "apikey": ALPHA_API_KEY
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params) as resp:
                data = await resp.json()
        ts_key = "Time Series (Digital Currency Daily)"
        if ts_key not in data:
            print(f"⚠️ Nuk u morën të dhëna daily për {symbol} nga Alpha Vantage")
            return None
        df = pd.DataFrame.from_dict(data[ts_key], orient="index")
        print(f"Kolonat origjinale për {symbol} crypto: {list(df.columns)}")

        rename_map = {
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. volume': 'Volume'
        }
        df = df.rename(columns=rename_map)
        print(f"Kolonat pas riemërtimit për {symbol} crypto: {list(df.columns)}")

        required_cols = ['Open', 'High', 'Low', 'Close']
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            print(f"❌ Mungojnë kolona të domosdoshme për {symbol}: {missing}")
            return None

        df = df[required_cols + ['Volume']].astype(float)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        return df

    else:
        # Forex
        if interval == "DAILY":
            function = "FX_DAILY"
            params = {
                "function": function,
                "from_symbol": symbol[:3],
                "to_symbol": symbol[3:],
                "outputsize": "compact",
                "apikey": ALPHA_API_KEY
            }
        else:
            function = "FX_INTRADAY"
            params = {
                "function": function,
                "from_symbol": symbol[:3],
                "to_symbol": symbol[3:],
                "interval": interval.lower(),
                "outputsize": "compact",
                "apikey": ALPHA_API_KEY
            }
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params) as resp:
                data = await resp.json()

        if interval == "DAILY":
            ts_key = "Time Series FX (Daily)"
        else:
            ts_key = f"Time Series FX ({interval})"
        if ts_key not in data:
            print(f"⚠️ Nuk u morën të dhëna {interval.lower()} për {symbol}")
            return None
        df = pd.DataFrame.from_dict(data[ts_key], orient="index")
        rename_map = {
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. volume': 'Volume'
        }
        df = df.rename(columns=rename_map)

        required_cols = ['Open', 'High', 'Low', 'Close']
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            print(f"❌ Mungojnë kolona të domosdoshme për {symbol}: {missing}")
            return None

        df = df[required_cols + ['Volume']].astype(float)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        return df

async def get_tv_screenshot(symbol, interval):
    url = f"https://www.tradingview.com/chart/?symbol={symbol}:{interval}"
    browser = await launch(headless=True, args=["--no-sandbox"])
    page = await browser.newPage()
    await page.goto(url)
    await asyncio.sleep(5)
    screenshot = await page.screenshot()
    await browser.close()
    return screenshot

def analyze_signals(df):
    close = df['Close'].values
    high = df['High'].values
    low = df['Low'].values

    ema_50 = ta.EMA(close, timeperiod=50)
    ema_200 = ta.EMA(close, timeperiod=200)
    rsi = ta.RSI(close, timeperiod=14)
    atr = ta.ATR(high, low, close, timeperiod=14)

    latest = -1
    signal = None

    if ema_50[latest] > ema_200[latest]:
        trend = "Bullish"
    else:
        trend = "Bearish"

    if rsi[latest] < 30 and trend == "Bullish":
        signal = "BUY"
    elif rsi[latest] > 70 and trend == "Bearish":
        signal = "SELL"
    else:
        signal = "HOLD"

    sl = None
    tp = None
    rr = None
    if signal == "BUY":
        sl = close[latest] - 1.5 * atr[latest]
        tp = close[latest] + 3 * atr[latest]
        rr = (tp - close[latest]) / (close[latest] - sl)
    elif signal == "SELL":
        sl = close[latest] + 1.5 * atr[latest]
        tp = close[latest] - 3 * atr[latest]
        rr = (close[latest] - tp) / (sl - close[latest])

    return {
        "signal": signal,
        "trend": trend,
        "rsi": rsi[latest],
        "ema_50": ema_50[latest],
        "ema_200": ema_200[latest],
        "sl": sl,
        "tp": tp,
        "rr": rr,
        "price": close[latest]
    }

async def send_telegram_signal(pair, analysis, screenshot_bytes):
    message = (
        f"📊 Sinjal Trading për {pair}\n"
        f"Trend: {analysis['trend']}\n"
        f"Sinjal: {analysis['signal']}\n"
        f"Çmimi aktual: {analysis['price']:.4f}\n"
        f"RSI: {analysis['rsi']:.2f}\n"
        f"EMA50: {analysis['ema_50']:.4f}\n"
        f"EMA200: {analysis['ema_200']:.4f}\n"
        f"SL: {analysis['sl']:.4f}\n"
        f"TP: {analysis['tp']:.4f}\n"
        f"Risk/Reward: {analysis['rr']:.2f}"
    )

    try:
        await bot.send_photo(
            chat_id=TELEGRAM_CHAT_ID,
            photo=BytesIO(screenshot_bytes),
            caption=message
        )
        print(f"✅ Sinjali u dërgua në Telegram për {pair}")
    except TelegramError as e:
        print(f"❌ Gabim gjatë dërgimit të sinjalit në Telegram: {e}")

async def analyze(pair):
    print(f"--- Analizoj {pair} ---")
    if eshte_fundjave(pair):
        print(f"⏸ {pair} nuk analizohet në fundjavë.")
        return

    df_daily = await get_data(pair, "DAILY")
    df_1h = await get_data(pair, "60min")

    if df_daily is None or df_1h is None:
        print(f"⚠️ Të dhënat mungojnë për {pair}")
        return

    analysis_daily = analyze_signals(df_daily)
    analysis_1h = analyze_signals(df_1h)

    screenshot = await get_tv_screenshot(pair, "1H")

    if analysis_1h['signal'] in ["BUY", "SELL"]:
        await send_telegram_signal(pair, analysis_1h, screenshot)
    else:
        print(f"Sinjal HOLD për {pair}, nuk dërgohet në Telegram.")

async def main_loop():
    print("[INFO] Bot po nis dhe do të punojë në loop të pafund...")
    while True:
        print(f"\n--- Nis analiza në {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} ---")
        try:
            tasks = [asyncio.create_task(analyze(pair)) for pair in PAIRS]
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"[ERROR] Gabim gjatë analizës: {e}")
        print("[INFO] Pushim 10 minuta para analizës tjetër...\n")
        await asyncio.sleep(600)  # 10 minuta

if __name__ == "__main__":
    asyncio.run(main_loop())

