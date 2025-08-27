from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Whale API is live. Use /history to get last 48 hours."}

@app.get("/whales_only")
def whales_only():
    # Always return some static test data
    return {
        "TEST_WHALE": [
            {
                "symbol": "TEST",
                "timestamp": "2025-08-27T00:00:00Z",
                "latest_volume": 123456,
                "average_volume": 1000,
                "whale_detected": True
            }
        ]
    }
