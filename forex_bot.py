import asyncio
import yfinance as yf
import numpy as np
import pandas as pd
import datetime
from telegram import Bot
import os
from dotenv import load_dotenv

# Ngarko variablat e ambientit
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
bot = Bot(token=TELEGRAM_TOKEN)

SYMBOLS = {
    "AUDCAD": "AUDCAD=X",
    "EURUSD": "EURUSD=X",
    "XAUUSD": "XAUUSD=X",
    "BTCUSD": "BTC-USD",
}

# Memorizo sinjalet për të shmangur dublikimin
sent_signals = set()

def calculate_ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

def is_weekend():
    weekday = datetime.datetime.utcnow().weekday()
    return weekday >= 5  # 5=Saturday, 6=Sunday

async def send_telegram_message(text):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        print(f"Gabim gjatë dërgimit në Telegram: {e}")

async def analyze_symbol(name, ticker):
    print(f"\n--- Analizoj {name} ---")

    if is_weekend() and "BTC" not in ticker:
        print(f"Sot është fundjavë, {ticker} nuk analizohet.")
        return

    df_daily = yf.download(ticker, period="1mo", interval="1d", progress=False, auto_adjust=True)
    df_1h = yf.download(ticker, period="7d", interval="60m", progress=False, auto_adjust=True)

    if df_daily.empty or df_1h.empty:
        print(f"Të dhënat nuk janë të mjaftueshme për {ticker}.")
        return

    ema_daily = calculate_ema(df_daily['Close'], span=20)
    rsi_daily = calculate_rsi(df_daily['Close'])
    atr_daily = calculate_atr(df_daily)

    ema_1h = calculate_ema(df_1h['Close'], span=20)
    rsi_1h = calculate_rsi(df_1h['Close'])

    try:
        ema_daily_val = ema_daily.iloc[-1].item()
        rsi_daily_val = rsi_daily.iloc[-1].item()
        atr_daily_val = atr_daily.iloc[-1].item()
        ema_1h_val = ema_1h.iloc[-1].item()
        rsi_1h_val = rsi_1h.iloc[-1].item()
        current_price = df_1h['Close'].iloc[-1].item()
    except:
        print(f"Vlera të paplota (NaN) për {ticker}, skipohet.")
        return

    print(f"EMA daily: {ema_daily_val:.2f}, RSI daily: {rsi_daily_val:.2f}")
    print(f"EMA 1H: {ema_1h_val:.2f}, RSI 1H: {rsi_1h_val:.2f}")
    print(f"ATR daily: {atr_daily_val:.2f}, Current price: {current_price:.2f}")

    buy_signal = (current_price > ema_daily_val and rsi_daily_val > 50) and (rsi_1h_val < 30 and current_price > ema_1h_val)
    sell_signal = (current_price < ema_daily_val and rsi_daily_val < 50) and (rsi_1h_val > 70 and current_price < ema_1h_val)

    signal_id = f"{name}-{datetime.datetime.utcnow().strftime('%Y-%m-%d-%H')}"

    if buy_signal and signal_id not in sent_signals:
        msg = f"📈 Buy Signal për {name}!\nÇmimi aktual: {current_price:.2f}\nEMA daily: {ema_daily_val:.2f}, RSI daily: {rsi_daily_val:.2f}"
        print(msg)
        await send_telegram_message(msg)
        sent_signals.add(signal_id)

    elif sell_signal and signal_id not in sent_signals:
        msg = f"📉 Sell Signal për {name}!\nÇmimi aktual: {current_price:.2f}\nEMA daily: {ema_daily_val:.2f}, RSI daily: {rsi_daily_val:.2f}"
        print(msg)
        await send_telegram_message(msg)
        sent_signals.add(signal_id)
    else:
        print("Nuk ka sinjal të ri ose është dërguar më parë.")

async def analyze_all():
    for name, ticker in SYMBOLS.items():
        await analyze_symbol(name, ticker)

async def main_loop():
    while True:
        print(f"\n⏱️ Fillon cikli i analizës: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        await analyze_all()
        print("✅ Cikli i analizës përfundoi. Pritet 1 orë...\n")
        await asyncio.sleep(3600)

async def start():
    print("🚀 Bot është online...")
    await send_telegram_message("🤖 Forex Bot është online!")
    await main_loop()

if __name__ == "__main__":
    asyncio.run(start())
