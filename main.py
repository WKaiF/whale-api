import os
import requests
from fastapi import FastAPI
from datetime import datetime, timedelta

app = FastAPI()

API_KEY = os.getenv("FMP_API_KEY")  # Your Financial Modeling Prep API key

# List of 100 symbols (you can add the rest)
STOCKS = [
    "AAPL","MSFT","GOOGL","AMZN","TSLA","NVDA","META","BRK.B","JNJ","V",
    # ... add remaining symbols up to 100
]

history_data = {}

def fetch_stock_data(symbol):
    """
    Fetch the latest stock volume and compute average volume.
    Use historical 1-hour data to calculate a real average.
    """
    url = f"https://financialmodelingprep.com/api/v3/historical-chart/1hour/{symbol}?apikey={API_KEY}"
    resp = requests.get(url)
    if resp.status_code == 200 and resp.json():
        data = resp.json()
        latest_volume = data[-1]["volume"] if data else 0

        # Calculate average volume from last 24 hours
        volumes = [entry["volume"] for entry in data]
        average_volume = sum(volumes) / len(volumes) if volumes else 1

        whale_detected = latest_volume > average_volume * 1

        return {
            "symbol": symbol,
            "latest_volume": latest_volume,
            "average_volume": average_volume,
            "whale_detected": whale_detected
        }
    return None

def update_history():
    """
    Fetch data for all stocks and update history.
    Keeps last 48 hours only.
    """
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

        # Keep only last 48 hours
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
    # RETURN EVERYTHING, skip the whale filter
    return history_data
