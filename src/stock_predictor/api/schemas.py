"""Pydantic schemas for API."""
from pydantic import BaseModel
from typing import List, Optional

class PredictionRequest(BaseModel):
    symbol: str
    days: int = 1  # not used in this simple version, but for future

class PredictionResponse(BaseModel):
    symbol: str
    predicted_price: float
    last_actual_price: float