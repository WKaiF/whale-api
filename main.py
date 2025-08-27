import os
import requests
from fastapi import FastAPI
from datetime import datetime, timedelta

app = FastAPI()

API_KEY = os.getenv("FMP_API_KEY")  # use your FMP API key

STOCKS = [
    "AAPL","MSFT","GOOGL","AMZN","TSLA","NVDA","META","BRK.B","JNJ","V",
    # ... add the rest to make 100
]

history_data = {}

def fetch_stock_data(symbol):
    # FMP endpoint for real-time stock volume/price data
    url = f"https://financialmodelingprep.com/api/v3/quote-short/{symbol}?apikey={API_KEY}"
    resp = requests.get(url)
    if resp.status_code == 200 and resp.json():
        data = resp.json()[0]
        latest_volume = data.get("volume", 0)
        # For simplicity, let's assume average volume = latest / 2 (or fetch another FMP endpoint)
        average_volume = latest_volume / 2 if latest_volume else 1
        whale_detected = latest_volume > average_volume * 2
        return {
            "symbol": symbol,
            "latest_volume": latest_volume,
            "average_volume": average_volume,
            "whale_detected": whale_detected
        }
    return None

def update_history():
    now = datetime.utcnow()
    for symbol in STOCKS:
        data = fetch_stock_data(symbol)
        if not data:
            continue
        if symbol not in history_data:
            history_data[symbol] = []
        history_data[symbol].append({
            "symbol": symbol,
            "timestamp": now.isoformat(),
            **data
        })
        cutoff = now - timedelta(hours=48)
        history_data[symbol] = [
            record for record in history_data[symbol]
            if datetime.fromisoformat(record["timestamp"]) >= cutoff
        ]

@app.get("/")
def root():
    return {"message": "Whale API is live. Use /history to get last 48 hours."}

@app.get("/history")
def get_history():
    update_history()
    return history_data

@app.get("/whales_only")
def whales_only():
    update_history()
    return {symbol: records for symbol, records in history_data.items() if records[-1]["whale_detected"]}
