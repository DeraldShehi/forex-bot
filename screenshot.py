import asyncio
from pyppeteer import launch
import os

# Funksioni real për të marrë screenshot nga TradingView
async def get_tv_screenshot(pair):
    symbol_map = {
        "EURUSD": "FX:EURUSD",
        "AUDCAD": "FX:AUDCAD",
        "XAUUSD": "OANDA:XAUUSD",
        "BTCUSD": "BINANCE:BTCUSDT"
    }

    tradingview_symbol = symbol_map.get(pair.upper(), None)
    if not tradingview_symbol:
        print(f"⚠️ Nuk u gjet simboli për {pair}")
        return None

    url = f"https://www.tradingview.com/chart/?symbol={tradingview_symbol}"

    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.setViewport({"width": 1280, "height": 720})
    await page.goto(url)
    await asyncio.sleep(10)  # jep kohë që të ngarkohet plotësisht grafiku

    screenshot_bytes = await page.screenshot()
    await browser.close()

    return screenshot_bytes
