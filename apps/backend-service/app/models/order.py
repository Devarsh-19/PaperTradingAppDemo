"""
Order model — buy/sell orders placed by users (market, limit, stop-loss).
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OrderType(str, enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"


class OrderSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )
    order_type: Mapped[OrderType] = mapped_column(
        Enum(OrderType),
        nullable=False,
    )
    side: Mapped[OrderSide] = mapped_column(
        Enum(OrderSide),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    filled_quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    price: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="Market price at time of order placement",
    )
    limit_price: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="Target price for LIMIT orders",
    )
    stop_price: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="Trigger price for STOP_LOSS orders",
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False,
        index=True,
    )
    reject_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    filled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ── Relationships ──
    user = relationship("User", back_populates="orders")
    portfolio = relationship("Portfolio", back_populates="orders")
    trades = relationship("Trade", back_populates="order", lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"<Order(id={self.id}, {self.side.value} {self.quantity} "
            f"{self.symbol} @ {self.order_type.value}, status={self.status.value})>"
        )
