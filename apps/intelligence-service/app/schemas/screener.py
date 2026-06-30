"""Pydantic schemas for the stock screener."""

from typing import Optional
from pydantic import BaseModel, Field


class ScreenerFilter(BaseModel):
    """Filters for the stock screener."""
    min_market_cap: Optional[float] = Field(None, description="Minimum market cap in USD")
    max_market_cap: Optional[float] = Field(None, description="Maximum market cap in USD")
    min_pe_ratio: Optional[float] = Field(None, description="Minimum P/E ratio")
    max_pe_ratio: Optional[float] = Field(None, description="Maximum P/E ratio")
    min_volume: Optional[int] = Field(None, description="Minimum daily volume")
    min_price: Optional[float] = Field(None, description="Minimum stock price")
    max_price: Optional[float] = Field(None, description="Maximum stock price")
    min_change_percent: Optional[float] = Field(None, description="Minimum % change today")
    max_change_percent: Optional[float] = Field(None, description="Maximum % change today")
    sector: Optional[str] = Field(None, description="Filter by sector")
    symbols: list[str] = Field(
        default=[
            "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM",
            "V", "JNJ", "WMT", "PG", "MA", "UNH", "HD", "DIS", "BAC", "XOM",
            "NFLX", "ADBE", "CRM", "CSCO", "INTC", "AMD", "PYPL",
        ],
        description="Universe of symbols to screen (defaults to top 25 US stocks)",
    )


class ScreenerResult(BaseModel):
    """A single stock result from the screener."""
    symbol: str
    name: Optional[str] = None
    price: float = 0
    change: float = 0
    change_percent: float = 0
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    sector: Optional[str] = None


class ScreenerResponse(BaseModel):
    """Response containing filtered screener results."""
    results: list[ScreenerResult]
    total: int
    filters_applied: int
