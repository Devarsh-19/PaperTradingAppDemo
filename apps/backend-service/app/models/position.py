"""
Position model — a holding of a specific stock within a portfolio.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
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
    quantity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    avg_buy_price: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    total_invested: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        doc="Total cost basis (qty × avg_buy_price at time of each purchase)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ──
    portfolio = relationship("Portfolio", back_populates="positions")

    def unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized profit/loss at a given market price."""
        return (current_price - self.avg_buy_price) * self.quantity

    def market_value(self, current_price: float) -> float:
        """Current market value of this position."""
        return current_price * self.quantity

    def __repr__(self) -> str:
        return f"<Position(symbol={self.symbol}, qty={self.quantity}, avg={self.avg_buy_price})>"
