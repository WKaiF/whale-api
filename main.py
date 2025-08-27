from fastapi import FastAPI, Query
import requests
import os
from datetime import datetime, timedelta

app = FastAPI()

API_KEY = os.getenv("WHALE_ALERT_KEY")

# Example: top 100 stocks (you can expand/change this list)
TOP_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK.B", "JPM", "JNJ",
    "V", "PG", "UNH", "HD", "MA", "DIS", "BAC", "ADBE", "PFE", "KO",
    "CMCSA", "PEP", "INTC", "CSCO", "XOM", "T", "VZ", "MRK", "CVX", "ORCL",
    "ABT", "CRM", "NKE", "WMT", "ACN", "MDT", "MCD", "DHR", "LLY", "BMY",
    "QCOM", "TXN", "COST", "NEE", "HON", "PM", "LIN", "UNP", "LOW", "IBM",
    "SBUX", "RTX", "AMGN", "MDLZ", "UPS", "INTU", "GS", "BLK", "CAT", "GE",
    "LMT", "BA", "MU", "CVS", "MMM", "BKNG", "ISRG", "NOW", "SPGI", "GILD",
    "FIS", "TMO", "SCHW", "SYK", "DE", "FISV", "ZTS", "ADI", "EL", "CCI",
    "MO", "VRTX", "WM", "APD", "SO", "BSX", "ICE", "TJX", "CSX", "CL",
    "ATVI", "EA", "ECL", "BDX", "HCA", "DUK", "EQIX", "ITW", "HUM", "PNC"
]

@app.get("/")
def root():
    return {"message": "Whale API is running!"}

def fetch_whale_alerts(tickers, min_value=500000):
    alerts = []
    for symbol in tickers:
        url = "https://api.whale-alert.io/v1/transactions"
        params = {
            "api_key": API_KEY,
            "currency": symbol,
            "min_value": min_value
        }
        try:
            res = requests.get(url, params=params)
            data = res.json()
            if "transactions" in data:
                alerts.extend(data["transactions"])
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
    return alerts

@app.get("/whale/latest")
def whale_latest(min_value: int = 500000):
    """
    Get latest whale alerts for top tickers
    """
    alerts = fetch_whale_alerts(TOP_TICKERS, min_value=min_value)
    return {"latest_alerts": alerts}

@app.get("/whale/history")
def whale_history(hours: int = 24, min_value: int = 500000):
    """
    Get whale alerts from the past `hours` for top tickers
    """
    end_time = int(datetime.utcnow().timestamp())
    start_time = int((datetime.utcnow() - timedelta(hours=hours)).timestamp())
    alerts = []

    for symbol in TOP_TICKERS:
        url = "https://api.whale-alert.io/v1/transactions"
        params = {
            "api_key": API_KEY,
            "currency": symbol,
            "min_value": min_value,
            "start": start_time,
            "end": end_time
        }
        try:
            res = requests.get(url, params=params)
            data = res.json()
            if "transactions" in data:
                alerts.extend(data["transactions"])
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")

    return {"past_alerts": alerts}
