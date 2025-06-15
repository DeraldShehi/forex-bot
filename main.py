import asyncio
from data_fetch import get_data
from analysis import analyze_signals
from telegram_bot import send_telegram_signal
from screenshot import get_tv_screenshot
from utils import eshte_fundjave, eshte_gjate_sesioneve
import datetime
from dotenv import load_dotenv

load_dotenv()

PAIRS = ["AUDCAD", "EURUSD", "XAUUSD", "BTCUSD"]
max_daily_loss = -1.0  # në %
current_daily_pnl = 0.0

async def analyze(pair):
    global current_daily_pnl

    if not eshte_gjate_sesioneve(pair):
        print(f"⏸ {pair} nuk analizohet jashtë orarit të tregtimit.")
        return

    if pair == "BTCUSD":
        df_daily = await get_data("BTCUSD", "1d")
        df_hourly = await get_data("BTCUSD", "1h")
    else:
        df_daily = await get_data(pair, "D")
        df_hourly = await get_data(pair, "60")

    if df_daily is None or df_hourly is None:
        print(f"⚠️ Nuk u morën të dhëna për {pair}")
        return

    analysis = analyze_signals(df_daily, df_hourly)

    if analysis['signal'] == "HOLD":
        print(f"❕ {pair}: Pa sinjal për entry.")
        return

    if current_daily_pnl <= max_daily_loss:
        print(f"🛑 Limiti i humbjes ditore arritur. Nuk dërgohet sinjali.")
        return

    screenshot = await get_tv_screenshot(pair)
    await send_telegram_signal(pair, analysis, screenshot)

    rr = analysis.get('rr', 0) or 0
    if rr < 1:
        current_daily_pnl += -1.0
    else:
        current_daily_pnl += 1.5

async def loop():
    print("[INFO] Bot në punë (çdo 1 orë)...")
    while True:
        print(f"\n--- {datetime.datetime.utcnow()} ---")
        await asyncio.gather(*(analyze(p) for p in PAIRS))
        print("[INFO] Pushim 1 orë...\n")
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(loop())
