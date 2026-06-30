"""
Portfolio model — a user's virtual trading portfolio with cash balance.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        default="Default Portfolio",
        nullable=False,
    )
    cash_balance: Mapped[float] = mapped_column(
        Float,
        default=100_000.00,
        nullable=False,
    )
    reserved_balance: Mapped[float] = mapped_column(
        Float,
        default=0.00,
        nullable=False,
        doc="Cash reserved for pending limit/stop orders",
    )
    initial_balance: Mapped[float] = mapped_column(
        Float,
        default=100_000.00,
        nullable=False,
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
    user = relationship("User", back_populates="portfolios")
    positions = relationship("Position", back_populates="portfolio", lazy="selectin")
    orders = relationship("Order", back_populates="portfolio", lazy="selectin")

    @property
    def available_cash(self) -> float:
        """Cash available for new orders (total minus reserved)."""
        return self.cash_balance - self.reserved_balance

    def __repr__(self) -> str:
        return f"<Portfolio(id={self.id}, name={self.name}, cash={self.cash_balance})>"
