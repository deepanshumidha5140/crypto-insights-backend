import os
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from apscheduler.schedulers.background import BackgroundScheduler
from services.pricing import save_coin_list
from services.portfolio import load_portfolio

CACHE_PATH = "data/price_cache.json"
scheduler = BackgroundScheduler()


def get_ist_timestamp() -> str:
    """Get current time in IST timezone in ISO format."""
    return datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()


def fetch_valid_coin_list():
    """
    Fetch top 250 coins by market cap from CoinGecko and store their IDs.
    """
    url = "https://api.coingecko.com/api/v3/coins/markets"
    try:
        res = requests.get(url, params={
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 250,
            "page": 1,
        })
        res.raise_for_status()
        coins = res.json()
        coin_ids = [coin["id"] for coin in coins]
        save_coin_list(coin_ids)
        print("[INFO] [Scheduler] Popular coin list updated")
    except requests.RequestException as e:
        print(f"[ERROR] [Scheduler] Failed to fetch coin list: {e}")


def fetch_all_prices():
    """
    Fetch current prices for all coins present in the portfolio.
    Updates the price cache file with latest prices and timestamps.
    """
    portfolio = load_portfolio()
    coin_ids = list(portfolio.keys())
    if not coin_ids:
        print("[INFO] [Scheduler] No coins in portfolio, skipping price update")
        return

    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        res = requests.get(url, params={
            "vs_currency": "usd",
            "ids": ",".join(coin_ids)
        })
        res.raise_for_status()
        data = res.json()

        price_cache = {}
        for coin in data:
            price_cache[coin["id"]] = {
                "price": coin["current_price"],
                "last_updated": get_ist_timestamp()
            }

        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(price_cache, f, indent=2)
        print("[INFO] [Scheduler] Price cache updated")

    except requests.RequestException as e:
        print(f"[ERROR] [Scheduler] Failed to fetch prices: {e}")


def start_scheduler():
    """
    Starts the background scheduler and fetches initial coin list and prices.
    """
    print("[INFO] [Scheduler] Starting background tasks...")
    fetch_valid_coin_list()
    scheduler.add_job(fetch_all_prices, 'interval', seconds=60)
    scheduler.start()


def stop_scheduler():
    """
    Gracefully shuts down the background scheduler.
    """
    print("[INFO] [Scheduler] Stopping background tasks...")
    scheduler.shutdown()