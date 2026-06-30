"""
Market data schemas — response models for quotes, history, and search.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class QuoteResponse(BaseModel):
    """Real-time quote for a single symbol."""
    symbol: str
    name: Optional[str] = None
    price: float
    previous_close: Optional[float] = None
    open: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    volume: Optional[int] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    market_cap: Optional[float] = None
    timestamp: Optional[datetime] = None


class BatchQuoteRequest(BaseModel):
    """Request batch quotes for multiple symbols."""
    symbols: list[str]


class CandleResponse(BaseModel):
    """Single OHLCV candle data point."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class HistoryResponse(BaseModel):
    """Historical OHLCV data for charting."""
    symbol: str
    interval: str
    candles: list[CandleResponse]


class SymbolSearchResult(BaseModel):
    """Symbol search autocomplete result."""
    symbol: str
    name: str
    exchange: Optional[str] = None
    type: Optional[str] = None


class MarketMover(BaseModel):
    """A trending stock (top gainer/loser/most active)."""
    symbol: str
    name: Optional[str] = None
    price: float
    change: float
    change_percent: float
    volume: Optional[int] = None


class TrendingResponse(BaseModel):
    """Top market movers."""
    gainers: list[MarketMover]
    losers: list[MarketMover]
    most_active: list[MarketMover]
