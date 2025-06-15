import asyncio
from pyppeteer import launch

async def get_tv_screenshot(symbol):
    url = f"https://www.tradingview.com/chart/?symbol={symbol}"
    browser = await launch(headless=True, args=["--no-sandbox"])
    page = await browser.newPage()
    await page.setViewport({"width": 1280, "height": 720})
    await page.goto(url)
    await asyncio.sleep(6)  # Prisni pak për ngarkimin e plotë
    screenshot = await page.screenshot()
    await browser.close()
    return screenshot
