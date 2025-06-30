from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models.schema import CoinAddRequest, CoinRemoveRequest
from services.pricing import get_price, get_all_valid_coins
from services.portfolio import add_coin, remove_coin, get_portfolio_with_value
from tasks.scheduler import start_scheduler, stop_scheduler
import json
import logging

# === Logging Setup ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Lifespan context ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    logger.info("[Startup] Scheduler started")
    yield
    stop_scheduler()
    logger.info("[Shutdown] Scheduler stopped")

# === App Init ===
app = FastAPI(
    title="Crypto Insights API",
    lifespan=lifespan,
)

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# === Root ===
@app.get("/", tags=["Health"])
def root():
    return {"message": "Crypto Insights API is live"}

# === Coins ===
@app.get("/coins", tags=["Coins"])
def get_coins():
    return get_all_valid_coins()

# === Portfolio: Add Coin ===
@app.post("/portfolio/add", tags=["Portfolio"])
def add_to_portfolio(req: CoinAddRequest):
    try:
        add_coin(req.coin_id, req.amount)
        return {"message": f"Added {req.amount} {req.coin_id} to portfolio"}
    except ValueError as e:
        logger.warning(f"Add coin failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# === Portfolio: Remove Coin ===
@app.post("/portfolio/remove", tags=["Portfolio"])
def remove_from_portfolio(req: CoinRemoveRequest):
    try:
        remove_coin(req.coin_id, req.amount)
        return {"message": f"Removed {req.amount} {req.coin_id} from portfolio"}
    except ValueError as e:
        logger.warning(f"Remove coin failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# === Portfolio: Get Full Portfolio ===
@app.get("/portfolio", tags=["Portfolio"])
def get_portfolio():
    return get_portfolio_with_value()

# === View Price Cache ===
@app.get("/get-price-cache", tags=["Debug"])
def view_cache():
    try:
        with open("data/price_cache.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load price cache: {e}")
        raise HTTPException(status_code=500, detail="Cache not available")

# This block ensures proper launch on Railway (or locally via `python main.py`)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)