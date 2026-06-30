"""
Trade model — immutable record of an executed order fill.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.order import OrderSide


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )
    side: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    execution_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    total_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="quantity × execution_price",
    )
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ──
    order = relationship("Order", back_populates="trades")
    user = relationship("User", back_populates="trades")

    def __repr__(self) -> str:
        return (
            f"<Trade(id={self.id}, {self.side} {self.quantity} "
            f"{self.symbol} @ {self.execution_price})>"
        )
