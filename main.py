from fastapi import FastAPI
import requests
import os

app = FastAPI()

API_KEY = os.getenv("WHALE_ALERT_KEY")

@app.get("/")
def root():
    return {"message": "Whale API is running!"}

@app.get("/whale")
def get_whale_alerts(currency: str = "btc", min_value: int = 500000):
    """
    Fetch whale alerts for a given currency
    Example: /whale?currency=eth&min_value=1000000
    """
    url = "https://api.whale-alert.io/v1/transactions"
    params = {
        "api_key": API_KEY,
        "min_value": min_value,
        "currency": currency
    }
    res = requests.get(url, params=params)
    return res.json()
