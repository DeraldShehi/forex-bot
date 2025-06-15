# Forex + BTC Signal Bot 📈📤

Ky bot analizon çiftet Forex dhe BTC/USD duke përdorur analizë teknike dhe dërgon sinjale në Telegram çdo orë.

## Teknologji

- Python 3.10+
- aiohttp
- pandas, numpy
- ta (technical analysis)
- Telegram Bot API
- TwelveData API (për Forex)
- Binance API (për BTC)

## Deploy në Render

1. Shto `.env` keys si `Environment Variables`:
   - `TELEGRAM_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `TWELVEDATA_API_KEY`
2. Shto këto file:
   - `requirements.txt`
   - `render.yaml`
3. Deploy repo-n në Render si **Background Worker**.
