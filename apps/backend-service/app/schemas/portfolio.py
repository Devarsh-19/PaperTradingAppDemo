"""
Portfolio schemas — response models for portfolio, positions, and trade history.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ── Position ──

class PositionResponse(BaseModel):
    """A single stock holding within a portfolio."""
    id: uuid.UUID
    symbol: str
    quantity: int
    avg_buy_price: float
    total_invested: float
    current_price: Optional[float] = None
    market_value: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    unrealized_pnl_percent: Optional[float] = None
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Portfolio Summary ──

class PortfolioSummaryResponse(BaseModel):
    """High-level portfolio overview with P&L."""
    portfolio_id: uuid.UUID
    name: str
    cash_balance: float
    reserved_balance: float
    available_cash: float
    invested_value: float
    market_value: float
    total_value: float
    total_pnl: float
    total_pnl_percent: float
    day_pnl: Optional[float] = None
    positions_count: int


# ── Trade History ──

class TradeResponse(BaseModel):
    """A single executed trade."""
    id: uuid.UUID
    order_id: uuid.UUID
    symbol: str
    side: str
    quantity: int
    execution_price: float
    total_value: float
    executed_at: datetime

    model_config = {"from_attributes": True}


class TradeListResponse(BaseModel):
    """Paginated trade history."""
    trades: list[TradeResponse]
    total: int
    page: int
    page_size: int


# ── Portfolio History (for equity curve) ──

class PortfolioSnapshotResponse(BaseModel):
    """Daily portfolio value snapshot for charting."""
    date: datetime
    total_value: float
    cash_balance: float
    invested_value: float
