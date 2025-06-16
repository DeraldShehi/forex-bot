import aiohttp
import asyncio
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")


async def get_data_twelvedata(symbol: str, interval: str):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "apikey": TWELVEDATA_API_KEY,
        "format": "JSON",
        "outputsize": 30,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            if "values" not in data:
                print(f"⚠️ Twelvedata error për {symbol}: {data.get('message', 'Pa të dhëna')}")
                return None

            values = data["values"]
            # Kthejmë në DataFrame dhe konvertojmë në formatin e duhur
            df = pd.DataFrame(values)
            df.rename(columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
                "datetime": "Timestamp"
            }, inplace=True)
            float_columns = ["Open", "High", "Low", "Close"]
            if "Volume" in df.columns:
                float_columns.append("Volume")

            df[float_columns] = df[float_columns].astype(float)
            df["Timestamp"] = pd.to_datetime(df["Timestamp"])
            df.sort_values("Timestamp", inplace=True)
            df.set_index("Timestamp", inplace=True)
            return df

async def get_data_binance(symbol: str, interval: str):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": 30,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            if isinstance(data, dict) and data.get("code"):
                print(f"⚠️ Binance error për {symbol}: {data.get('msg', '')}")
                return None

            df = pd.DataFrame(data, columns=[
                "OpenTime", "Open", "High", "Low", "Close", "Volume",
                "CloseTime", "QuoteAssetVolume", "NumberOfTrades",
                "TakerBuyBaseVolume", "TakerBuyQuoteVolume", "Ignore"
            ])
            df["Timestamp"] = pd.to_datetime(df["OpenTime"], unit='ms')
            df[["Open", "High", "Low", "Close", "Volume"]] = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)
            df = df[["Timestamp", "Open", "High", "Low", "Close", "Volume"]]
            df.sort_values("Timestamp", inplace=True)
            df.set_index("Timestamp", inplace=True)
            return df

async def get_data(pair: str, interval: str):
    interval_map_binance = {
        "D": "1d",
        "60": "1h",
        "1d": "1d",
        "1h": "1h",
    }

    interval_map_twelvedata = {
        "D": "1day",
        "60": "1h",
        "1d": "1day",
        "1h": "1h",
    }

    if pair == "BTCUSD":
        binance_interval = interval_map_binance.get(interval, "1h")
        return await get_data_binance("BTCUSDT", binance_interval)

    symbol_map = {
        "EURUSD": "EUR/USD",
        "AUDCAD": "AUD/CAD",
        "XAUUSD": "XAU/USD",
    }

    tw_symbol = symbol_map.get(pair)
    if not tw_symbol:
        print(f"⚠️ Symbol {pair} nuk gjendet në mappim Twelvedata.")
        return None

    tw_interval = interval_map_twelvedata.get(interval, "1day")
    return await get_data_twelvedata(tw_symbol, tw_interval)
