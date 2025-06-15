import ta
import pandas as pd

def calculate_support_resistance(df):
    # Shtojmë një mënyrë të thjeshtë për support dhe resistance (p.sh., pivot points)
    pivots = {}
    pivots['pivot'] = (df['High'].iloc[-1] + df['Low'].iloc[-1] + df['Close'].iloc[-1]) / 3
    pivots['support1'] = 2 * pivots['pivot'] - df['High'].iloc[-1]
    pivots['resistance1'] = 2 * pivots['pivot'] - df['Low'].iloc[-1]
    return pivots

def calculate_aoi_demand_supply(df):
    # AOI dhe Demand/Supply zone kërkojnë modele më komplekse,
    # për shembull zona ku ka konfluencë volume + çmime ose zona ku kemi candle me body të madh
    # Për këtë shembull do të përdorim candle me body të madh si zonë demand/supply

    df['body_size'] = (df['Close'] - df['Open']).abs()
    # Merrni 3 candles me body më të madh (simplifikim)
    top_bodies = df.nlargest(3, 'body_size')
    zones = list(zip(top_bodies['Low'], top_bodies['High']))
    return zones

def analyze_candlestick_patterns(df):
    # Shembull i thjeshtë: Engulfing pattern
    last = df.iloc[-1]
    prev = df.iloc[-2]
    bullish_engulfing = (last['Close'] > last['Open']) and (prev['Close'] < prev['Open']) and (last['Close'] > prev['Open']) and (last['Open'] < prev['Close'])
    bearish_engulfing = (last['Close'] < last['Open']) and (prev['Close'] > prev['Open']) and (last['Open'] > prev['Close']) and (last['Close'] < prev['Open'])
    if bullish_engulfing:
        return "Bullish Engulfing"
    elif bearish_engulfing:
        return "Bearish Engulfing"
    return None

def analyze_signals(df_daily, df_1h):
    close_d = df_daily['Close']
    close_1h = df_1h['Close']
    high_1h = df_1h['High']
    low_1h = df_1h['Low']

    ema_50 = ta.trend.ema_indicator(close_d, window=50).fillna(0)
    ema_200 = ta.trend.ema_indicator(close_d, window=200).fillna(0)
    rsi = ta.momentum.rsi(close_1h, window=14).fillna(0)
    macd = ta.trend.macd(close_1h).fillna(0)
    macd_signal = ta.trend.macd_signal(close_1h).fillna(0)

    atr = ta.volatility.average_true_range(high_1h, low_1h, close_1h, window=14).fillna(0)

    pivots = calculate_support_resistance(df_1h)
    zones = calculate_aoi_demand_supply(df_1h)
    candle_pattern = analyze_candlestick_patterns(df_1h)

    latest = -1
    trend = "Bullish" if ema_50.iloc[-1] > ema_200.iloc[-1] else "Bearish"

    signal = "HOLD"

    # Strategji e thjeshtë me EMA, RSI, MACD dhe candle pattern
    if trend == "Bullish" and rsi.iloc[latest] < 30 and macd.iloc[latest] > macd_signal.iloc[latest]:
        signal = "BUY"
        if candle_pattern:
            signal += f" ({candle_pattern})"
    elif trend == "Bearish" and rsi.iloc[latest] > 70 and macd.iloc[latest] < macd_signal.iloc[latest]:
        signal = "SELL"
        if candle_pattern:
            signal += f" ({candle_pattern})"

    sl = tp = rr = None
    price = close_1h.iloc[latest]

    if signal.startswith("BUY"):
        sl = price - 1.5 * atr.iloc[latest]
        tp = price + 3 * atr.iloc[latest]
        rr = (tp - price) / (price - sl)
    elif signal.startswith("SELL"):
        sl = price + 1.5 * atr.iloc[latest]
        tp = price - 3 * atr.iloc[latest]
        rr = (price - tp) / (sl - price)

    return {
        "signal": signal,
        "trend": trend,
        "price": price,
        "rsi": rsi.iloc[latest],
        "ema_50": ema_50.iloc[-1],
        "ema_200": ema_200.iloc[-1],
        "sl": sl,
        "tp": tp,
        "rr": rr,
        "pivots": pivots,
        "zones": zones,
        "candle_pattern": candle_pattern
    }
