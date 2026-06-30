"""Pydantic schemas for technical indicators."""

from typing import Optional
from pydantic import BaseModel


class MovingAverage(BaseModel):
    period: int
    value: Optional[float] = None


class MACDResult(BaseModel):
    macd_line: Optional[float] = None
    signal_line: Optional[float] = None
    histogram: Optional[float] = None


class IndicatorsResponse(BaseModel):
    """Technical indicators for a symbol."""
    symbol: str
    price: float = 0
    sma: list[MovingAverage] = []
    ema: list[MovingAverage] = []
    rsi_14: Optional[float] = None
    macd: Optional[MACDResult] = None
    atr_14: Optional[float] = None
    volume_avg_20: Optional[int] = None
