import json
import os
from typing import Optional, Dict, Any, List

CACHE_PATH = "data/price_cache.json"
COIN_LIST_PATH = "data/coin_list.json"

def get_cached_price(coin_id: str) -> Optional[float]:
    """
    Retrieve a cached price for a specific coin.
    Returns None if not found or cache is unavailable.
    """
    if not os.path.exists(CACHE_PATH):
        return None

    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            cache: Dict[str, Dict[str, Any]] = json.load(f)
            entry = cache.get(coin_id)
            if entry and "price" in entry:
                return entry["price"]
    except (json.JSONDecodeError, FileNotFoundError):
        pass

    return None

def get_price(coin_id: str) -> Optional[float]:
    """
    Public accessor for coin price.
    """
    return get_cached_price(coin_id)

def save_coin_list(coins: List[str]) -> None:
    """
    Save the list of valid coins to disk.
    """
    os.makedirs(os.path.dirname(COIN_LIST_PATH), exist_ok=True)
    with open(COIN_LIST_PATH, "w", encoding="utf-8") as f:
        json.dump(coins, f, indent=2)

def load_coin_list() -> List[str]:
    """
    Load the list of valid coins from disk.
    Returns an empty list if not available or corrupted.
    """
    if not os.path.exists(COIN_LIST_PATH):
        return []

    try:
        with open(COIN_LIST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def get_all_valid_coins() -> List[str]:
    """
    Return all valid coin IDs for selection.
    """
    return load_coin_list()