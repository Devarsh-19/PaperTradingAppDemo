"""
Leaderboard service — ranks users by portfolio performance.
"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import Portfolio
from app.models.position import Position
from app.models.user import User
from app.services.market_data_service import MarketDataService

from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    """A single leaderboard entry."""
    rank: int
    user_id: uuid.UUID
    username: str
    total_value: float
    total_pnl: float
    total_pnl_percent: float
    positions_count: int


class LeaderboardResponse(BaseModel):
    """Full leaderboard."""
    entries: list[LeaderboardEntry]
    total_users: int


class LeaderboardService:
    """Ranks users by portfolio performance."""

    def __init__(self, db: AsyncSession, market_data: MarketDataService):
        self.db = db
        self.market_data = market_data

    async def get_leaderboard(self, limit: int = 50) -> LeaderboardResponse:
        """
        Get the global leaderboard ranked by total portfolio value.

        Fetches all users' default portfolios, calculates live values,
        and returns ranked results.
        """
        # Fetch all active users with their default portfolios
        result = await self.db.execute(
            select(User, Portfolio)
            .join(Portfolio, Portfolio.user_id == User.id)
            .where(User.is_active == True)
            .order_by(Portfolio.created_at.asc())
        )
        rows = result.all()

        # Collect all unique symbols across all portfolios
        all_symbols = set()
        portfolio_positions: dict[uuid.UUID, list[Position]] = {}

        for user, portfolio in rows:
            pos_result = await self.db.execute(
                select(Position).where(Position.portfolio_id == portfolio.id)
            )
            positions = pos_result.scalars().all()
            portfolio_positions[portfolio.id] = positions
            for pos in positions:
                all_symbols.add(pos.symbol)

        # Batch fetch prices
        price_map = {}
        if all_symbols:
            quotes = await self.market_data.get_batch_quotes(list(all_symbols))
            price_map = {q.symbol: q.price for q in quotes}

        # Calculate each user's total value
        entries = []
        for user, portfolio in rows:
            positions = portfolio_positions.get(portfolio.id, [])
            market_value = sum(
                pos.quantity * price_map.get(pos.symbol, pos.avg_buy_price)
                for pos in positions
            )
            total_value = portfolio.cash_balance + market_value
            total_pnl = total_value - portfolio.initial_balance
            total_pnl_pct = (
                (total_pnl / portfolio.initial_balance * 100)
                if portfolio.initial_balance > 0
                else 0
            )

            entries.append(
                LeaderboardEntry(
                    rank=0,  # Will set after sorting
                    user_id=user.id,
                    username=user.username,
                    total_value=round(total_value, 2),
                    total_pnl=round(total_pnl, 2),
                    total_pnl_percent=round(total_pnl_pct, 4),
                    positions_count=len(positions),
                )
            )

        # Sort by total value descending and assign ranks
        entries.sort(key=lambda e: e.total_value, reverse=True)
        for i, entry in enumerate(entries[:limit], start=1):
            entry.rank = i

        return LeaderboardResponse(
            entries=entries[:limit],
            total_users=len(entries),
        )

    async def get_user_rank(
        self,
        user_id: uuid.UUID,
    ) -> Optional[LeaderboardEntry]:
        """Get a specific user's rank on the leaderboard."""
        leaderboard = await self.get_leaderboard(limit=1000)
        for entry in leaderboard.entries:
            if entry.user_id == user_id:
                return entry
        return None
