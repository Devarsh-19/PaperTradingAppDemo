"""
Watchlist schemas — request/response models for watchlist management.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Request Schemas ──

class WatchlistCreateRequest(BaseModel):
    """Create a new watchlist."""
    name: str = Field(..., min_length=1, max_length=100)


class WatchlistAddSymbolRequest(BaseModel):
    """Add a symbol to a watchlist."""
    symbol: str = Field(..., min_length=1, max_length=20)


# ── Response Schemas ──

class WatchlistItemResponse(BaseModel):
    """Single item in a watchlist (with optional live price)."""
    id: uuid.UUID
    symbol: str
    added_at: datetime
    current_price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None

    model_config = {"from_attributes": True}


class WatchlistResponse(BaseModel):
    """A watchlist with its items."""
    id: uuid.UUID
    name: str
    created_at: datetime
    items: list[WatchlistItemResponse] = []

    model_config = {"from_attributes": True}
