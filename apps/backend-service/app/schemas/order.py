"""
Order schemas — request/response models for order placement and management.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.models.order import OrderSide, OrderStatus, OrderType


# ── Request Schemas ──

class OrderCreateRequest(BaseModel):
    """Place a new order."""
    symbol: str = Field(..., min_length=1, max_length=20, description="Stock ticker symbol")
    side: OrderSide
    order_type: OrderType
    quantity: int = Field(..., gt=0, description="Number of shares")
    limit_price: Optional[float] = Field(None, gt=0, description="Required for LIMIT orders")
    stop_price: Optional[float] = Field(None, gt=0, description="Required for STOP_LOSS orders")

    @model_validator(mode="after")
    def validate_prices(self):
        """Ensure limit/stop prices are provided for the correct order types."""
        if self.order_type == OrderType.LIMIT and self.limit_price is None:
            raise ValueError("limit_price is required for LIMIT orders")
        if self.order_type == OrderType.STOP_LOSS and self.stop_price is None:
            raise ValueError("stop_price is required for STOP_LOSS orders")
        return self


# ── Response Schemas ──

class OrderResponse(BaseModel):
    """Order detail response."""
    id: uuid.UUID
    user_id: uuid.UUID
    portfolio_id: uuid.UUID
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: int
    filled_quantity: int
    price: Optional[float] = None
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus
    reject_reason: Optional[str] = None
    created_at: datetime
    filled_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    """Paginated list of orders."""
    orders: list[OrderResponse]
    total: int
    page: int
    page_size: int
