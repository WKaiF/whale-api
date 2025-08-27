from fastapi import FastAPI
from datetime import datetime
import json

app = FastAPI()

# Load whale data dynamically from a file
def load_whale_data():
    with open("whale_data.json", "r") as f:
        return json.load(f)

@app.get("/")
def root():
    return {"message": "Whale API is live. Use /history to get last 24 hours."}

@app.get("/history")
def get_history():
    data = load_whale_data()
    return data

@app.get("/whales_only")
def whales_only():
    data = load_whale_data()
    return {symbol: info for symbol, info in data.items() if info[0]["whale_detected"]}
