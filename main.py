from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
import datetime
import random  # placeholder for actual whale detection API call

app = FastAPI()

# Top 100 US stocks by market cap (symbols)
TOP_100_STOCKS = [
    "AAPL","MSFT","GOOGL","AMZN","TSLA","NVDA","META","BRK.B","JNJ","V",
    "UNH","PG","MA","XOM","HD","PFE","CVX","KO","LLY","ABBV",
    "MRK","PEP","AVGO","COST","ORCL","TMO","CRM","MCD","ACN","NEE",
    "NKE","DHR","QCOM","TXN","BMY","LIN","WMT","AMD","LOW","MS",
    "SCHW","AMGN","UPS","PM","IBM","HON","SBUX","INTC","RTX","MDT",
    "BLK","CAT","NOW","BA","GILD","BKNG","GE","SPGI","LMT","C",
    "ADP","DE","ISRG","SYK","MO","PLD","T","FIS","TJX","TMUS",
    "CI","VRTX","FISV","ADI","ZTS","CB","MDLZ","MMC","EQIX","MU",
    "SCHW","ATVI","CSCO","APD","EW","CCI","REGN","HUM","ELV","PNC",
    "SO","ICE","ADBE","ECL","CL","FDX","ALL","NSC","MCO","ITW"
]

# In-memory store for historical data
stock_history = {ticker: [] for ticker in TOP_100_STOCKS}

def fetch_whale_data(ticker: str):
    # Replace this with your actual API call to detect whales
    return {
        "symbol": ticker,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "latest_volume": random.randint(1_000_000, 5_000_000),
        "average_volume": random.randint(500_000, 2_000_000),
        "whale_detected": random.choice([True, False])
    }

@app.on_event("startup")
@repeat_every(seconds=30*60)  # every 30 minutes
def update_stock_history():
    for ticker in TOP_100_STOCKS:
        data = fetch_whale_data(ticker)
        stock_history[ticker].append(data)
        # Keep only the last 48 intervals (~24 hours)
        if len(stock_history[ticker]) > 48:
            stock_history[ticker].pop(0)

@app.get("/history")
def get_history():
    """Return the last 24 hours (48 intervals) of 30-min whale data for all stocks."""
    return stock_history

@app.get("/")
def root():
    return {"message": "Whale API is live. Use /history to get last 24 hours."}
