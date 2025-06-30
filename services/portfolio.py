import json
import os
from typing import Dict
from services.pricing import get_price

PORTFOLIO_PATH = "data/portfolio_store.json"

# Ensure portfolio file exists
if not os.path.exists(PORTFOLIO_PATH):
    os.makedirs(os.path.dirname(PORTFOLIO_PATH), exist_ok=True)
    with open(PORTFOLIO_PATH, "w", encoding="utf-8") as f:
        json.dump({}, f)

def load_portfolio() -> Dict[str, float]:
    """
    Load the portfolio from disk. Returns empty dict if not found or corrupt.
    """
    try:
        with open(PORTFOLIO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_portfolio(data: Dict[str, float]) -> None:
    """
    Save the portfolio to disk.
    """
    with open(PORTFOLIO_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def add_coin(coin_id: str, amount: float) -> None:
    """
    Add or update a coin in the portfolio.
    """
    if amount <= 0:
        raise ValueError("Amount must be a positive number")

    data = load_portfolio()
    data[coin_id] = data.get(coin_id, 0) + amount
    save_portfolio(data)

def remove_coin(coin_id: str, amount: float) -> None:
    """
    Remove a coin amount from the portfolio.
    If total amount becomes 0, coin is removed completely.
    """
    if amount <= 0:
        raise ValueError("Amount must be a positive number")

    data = load_portfolio()
    if coin_id not in data:
        raise ValueError("Coin not present in portfolio")

    current_amount = data[coin_id]
    if amount < current_amount:
        data[coin_id] = current_amount - amount
    elif amount == current_amount:
        del data[coin_id]
    else:
        raise ValueError(f"Not enough {coin_id} in portfolio to remove {amount}")

    save_portfolio(data)

def get_portfolio_with_value() -> Dict[str, any]:
    """
    Get portfolio data with real-time value and total worth.
    Uses cached prices via get_price().
    """
    data = load_portfolio()
    result = {}
    total_value = 0.0

    for coin, amount in data.items():
        price = get_price(coin)
        if price is not None:
            value = round(amount * price, 2)
            result[coin] = {
                "amount": amount,
                "price": price,
                "value_usd": value
            }
            total_value += value
        else:
            result[coin] = {
                "amount": amount,
                "price": None,
                "value_usd": 0
            }

    result["total_portfolio_value"] = round(total_value, 2)
    return result