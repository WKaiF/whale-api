from fastapi import FastAPI
import requests
import os
import statistics

app = FastAPI()

API_KEY = os.getenv("FMP_API_KEY")

@app.get("/")
def root():
    return {"message": "Stock Whale API is running!"}

@app.get("/whale")
def get_stock_whales(symbol: str = "AAPL", interval: str = "30min"):
    """
    Detect whale-like activity for a given stock.
    Example: /whale?symbol=AAPL&interval=30min
    """
    url = f"https://financialmodelingprep.com/api/v3/historical-chart/{interval}/{symbol}"
    params = {"apikey": API_KEY}
    res = requests.get(url, params=params)
    data = res.json()

    if not isinstance(data, list) or len(data) < 10:
        return {"error": "Not enough data or invalid response"}

    # Get last 10 candles
    volumes = [candle["volume"] for candle in data[:10]]
    avg_volume = statistics.mean(volumes[1:])  # average of past 9
    latest_volume = volumes[0]

    whale_detected = latest_volume > 2 * avg_volume

    return {
        "symbol": symbol,
        "interval": interval,
        "latest_volume": latest_volume,
        "average_volume": avg_volume,
        "whale_detected": whale_detected,
    }
