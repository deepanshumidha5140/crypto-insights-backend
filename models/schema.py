from pydantic import BaseModel

class CoinAddRequest(BaseModel):
    coin_id: str
    amount: float

class CoinRemoveRequest(BaseModel):
    coin_id: str
    amount: float