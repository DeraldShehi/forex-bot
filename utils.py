import datetime

def eshte_fundjave(pair):
    now = datetime.datetime.utcnow()
    weekday = now.weekday()
    if pair == "BTCUSD":
        return False  # BTC është 24/7
    return weekday >= 5  # Sabtu e Diel

def eshte_gjate_sesioneve(pair):
    # London + NY session UTC:
    # London 08:00-16:00 UTC
    # New York 13:30-20:00 UTC
    now = datetime.datetime.utcnow().time()
    london_open = datetime.time(8, 0)
    london_close = datetime.time(16, 0)
    ny_open = datetime.time(13, 30)
    ny_close = datetime.time(20, 0)

    if pair == "BTCUSD":
        return True  # BTC 24/7
    if eshte_fundjave(pair):
        return False
    return (london_open <= now <= london_close) or (ny_open <= now <= ny_close)
