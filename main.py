from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi_utils.tasks import repeat_every
import requests
import os
import sqlite3
from datetime import datetime, timedelta

app = FastAPI()

API_KEY = os.getenv("WHALE_ALERT_KEY")  # your API key here
DB_FILE = "whale_alerts.db"

# Top 100 stock symbols
TOP_STOCKS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA",
    "NVDA", "META", "BRK.B", "JPM", "JNJ",
    "V", "PG", "UNH", "MA", "HD",
    "BAC", "XOM", "KO", "PFE", "MRK",
    "ABBV", "PEP", "WMT", "CVX", "DIS",
    "CSCO", "NFLX", "VZ", "ADBE", "CMCSA",
    "NKE", "ABT", "TMO", "CRM", "ACN",
    "MDT", "INTC", "COST", "MCD", "NEE",
    "TXN", "AMGN", "HON", "QCOM", "LIN",
    "BMY", "PM", "ORCL", "LOW", "SBUX",
    "RTX", "UPS", "IBM", "MS", "BLK",
    "DE", "CAT", "GE", "BA", "GS",
    "AMT", "SPGI", "NOW", "GILD", "CHTR",
    "ISRG", "SYK", "MDLZ", "LMT", "BKNG",
    "FIS", "ADI", "MU", "T", "CVS",
    "SCHW", "CCI", "ZTS", "PLD", "VRTX",
    "INTU", "FISV", "CME", "EL", "EQIX",
    "BIIB", "CSX", "CL", "SO", "PNC",
    "APD", "DUK", "ICE", "HUM", "MMC",
    "EMR", "ETN", "LRCX", "AON", "ADP",
    "GM", "MO", "ROST", "PGR", "BDX"
]

# Minimum volume to consider a whale trade (adjust as needed)
MIN_VOLUME = 1_000_000

# ---------------------------
# Database setup
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS whale_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            timestamp DATETIME,
            latest_volume INTEGER,
            average_volume REAL,
            whale_detected BOOLEAN
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------------------
# Helper functions
# ---------------------------
def fetch_volume(symbol: str):
    """
    Fetch latest trade volume for a stock symbol.
    Returns dict with latest_volume and average_volume.
    """
    # Replace this URL with a real API endpoint if you have one
    # For example, you could use IEX Cloud, Polygon, or Alpha Vantage
    url = f"https://api.whale-alert.io/v1/transactions"
    params = {
        "api_key": API_KEY,
        "currency": symbol.lower(),
        "min_value": MIN_VOLUME
    }
    try:
        res = requests.get(url, params=params)
        data = res.json()
        # For simplicity, using number of transactions as "volume"
        latest_volume = sum(tx["amount"] for tx in data.get("transactions", [])) if "transactions" in data else 0
        average_volume = latest_volume  # placeholder; ideally compute moving average
        whale_detected = latest_volume > average_volume
        return {
            "symbol": symbol,
            "latest_volume": latest_volume,
            "average_volume": average_volume,
            "whale_detected": whale_detected
        }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def save_alert(alert):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO whale_alerts (symbol, timestamp, latest_volume, average_volume, whale_detected)
        VALUES (?, ?, ?, ?, ?)
    """, (alert["symbol"], datetime.utcnow(), alert["latest_volume"], alert["average_volume"], alert["whale_detected"]))
    conn.commit()
    conn.close()

# ---------------------------
# Background task
# ---------------------------
@app.on_event("startup")
@repeat_every(seconds=30*60)  # every 30 minutes
def scan_whales_task():
    print("Running whale scan...")
    for symbol in TOP_STOCKS:
        alert = fetch_volume(symbol)
        if alert:
            save_alert(alert)
    print("Whale scan complete.")

# ---------------------------
# API endpoints
# ---------------------------
@app.get("/")
def root():
    return {"message": "Whale API is running!"}

@app.get("/whale/latest")
def get_latest_alerts():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Get the latest alert for each symbol
    c.execute("""
        SELECT symbol, latest_volume, average_volume, whale_detected, MAX(timestamp)
        FROM whale_alerts
        GROUP BY symbol
    """)
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append({
            "symbol": row[0],
            "latest_volume": row[1],
            "average_volume": row[2],
            "whale_detected": bool(row[3]),
            "timestamp": row[4]
        })
    return JSONResponse(result)

@app.get("/whale/history")
def get_whale_history(hours: int = 24):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    since = datetime.utcnow() - timedelta(hours=hours)
    c.execute("""
        SELECT symbol, timestamp, latest_volume, average_volume, whale_detected
        FROM whale_alerts
        WHERE timestamp >= ?
        ORDER BY timestamp DESC
    """, (since,))
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append({
            "symbol": row[0],
            "timestamp": row[1],
            "latest_volume": row[2],
            "average_volume": row[3],
            "whale_detected": bool(row[4])
        })
    return JSONResponse(result)
