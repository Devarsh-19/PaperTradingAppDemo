"""
Portfolio service — portfolio summary, positions, and trade history with live pricing.
"""

import uuid
from typing import Optional

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import Portfolio
from app.models.position import Position
from app.models.trade import Trade
from app.schemas.portfolio import (
    PortfolioSummaryResponse,
    PositionResponse,
    TradeListResponse,
    TradeResponse,
)
from app.services.market_data_service import MarketDataService


class PortfolioService:
    """Handles portfolio valuation, positions, and trade history."""

    def __init__(self, db: AsyncSession, market_data: MarketDataService):
        self.db = db
        self.market_data = market_data

    async def get_summary(
        self,
        user_id: uuid.UUID,
        portfolio_id: Optional[uuid.UUID] = None,
    ) -> PortfolioSummaryResponse:
        """
        Get a comprehensive portfolio summary with live P&L.

        Fetches current prices for all held positions and calculates
        total portfolio value, invested value, and unrealized P&L.
        """
        # Fetch portfolio (default if no ID specified)
        if portfolio_id:
            query = select(Portfolio).where(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == user_id,
            )
        else:
            query = select(Portfolio).where(
                Portfolio.user_id == user_id
            ).order_by(Portfolio.created_at.asc())

        result = await self.db.execute(query)
        portfolio = result.scalar_one_or_none()

        if not portfolio:
            raise ValueError("Portfolio not found")

        # Fetch all positions
        result = await self.db.execute(
            select(Position).where(Position.portfolio_id == portfolio.id)
        )
        positions = result.scalars().all()

        # Calculate live values
        invested_value = 0.0
        market_value = 0.0

        if positions:
            symbols = [p.symbol for p in positions]
            quotes = await self.market_data.get_batch_quotes(symbols)
            price_map = {q.symbol: q.price for q in quotes}

            for pos in positions:
                current_price = price_map.get(pos.symbol, pos.avg_buy_price)
                invested_value += pos.total_invested
                market_value += pos.quantity * current_price

        total_value = portfolio.cash_balance + market_value
        total_pnl = total_value - portfolio.initial_balance
        total_pnl_percent = (
            (total_pnl / portfolio.initial_balance * 100)
            if portfolio.initial_balance > 0
            else 0
        )

        return PortfolioSummaryResponse(
            portfolio_id=portfolio.id,
            name=portfolio.name,
            cash_balance=round(portfolio.cash_balance, 2),
            reserved_balance=round(portfolio.reserved_balance, 2),
            available_cash=round(portfolio.available_cash, 2),
            invested_value=round(invested_value, 2),
            market_value=round(market_value, 2),
            total_value=round(total_value, 2),
            total_pnl=round(total_pnl, 2),
            total_pnl_percent=round(total_pnl_percent, 4),
            positions_count=len(positions),
        )

    async def get_positions(
        self,
        user_id: uuid.UUID,
        portfolio_id: Optional[uuid.UUID] = None,
    ) -> list[PositionResponse]:
        """
        Get all positions with live price data and unrealized P&L.
        """
        # Fetch portfolio
        if portfolio_id:
            query = select(Portfolio).where(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == user_id,
            )
        else:
            query = select(Portfolio).where(
                Portfolio.user_id == user_id
            ).order_by(Portfolio.created_at.asc())

        result = await self.db.execute(query)
        portfolio = result.scalar_one_or_none()
        if not portfolio:
            raise ValueError("Portfolio not found")

        # Fetch positions
        result = await self.db.execute(
            select(Position).where(Position.portfolio_id == portfolio.id)
        )
        positions = result.scalars().all()

        if not positions:
            return []

        # Fetch live prices
        symbols = [p.symbol for p in positions]
        quotes = await self.market_data.get_batch_quotes(symbols)
        price_map = {q.symbol: q.price for q in quotes}

        responses = []
        for pos in positions:
            current_price = price_map.get(pos.symbol, pos.avg_buy_price)
            unrealized = pos.unrealized_pnl(current_price)
            unrealized_pct = (
                (unrealized / pos.total_invested * 100)
                if pos.total_invested > 0
                else 0
            )

            responses.append(
                PositionResponse(
                    id=pos.id,
                    symbol=pos.symbol,
                    quantity=pos.quantity,
                    avg_buy_price=round(pos.avg_buy_price, 4),
                    total_invested=round(pos.total_invested, 2),
                    current_price=round(current_price, 4),
                    market_value=round(pos.market_value(current_price), 2),
                    unrealized_pnl=round(unrealized, 2),
                    unrealized_pnl_percent=round(unrealized_pct, 4),
                    updated_at=pos.updated_at,
                )
            )

        return responses

    async def get_trades(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> TradeListResponse:
        """Get paginated trade history."""
        count_query = (
            select(func.count())
            .select_from(Trade)
            .where(Trade.user_id == user_id)
        )
        total = (await self.db.execute(count_query)).scalar()

        query = (
            select(Trade)
            .where(Trade.user_id == user_id)
            .order_by(Trade.executed_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.execute(query)
        trades = result.scalars().all()

        return TradeListResponse(
            trades=[TradeResponse.model_validate(t) for t in trades],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def reset_portfolio(
        self,
        user_id: uuid.UUID,
        portfolio_id: Optional[uuid.UUID] = None,
    ) -> PortfolioSummaryResponse:
        """
        Reset a portfolio to its initial balance.

        Deletes all positions and resets cash to initial_balance.
        """
        if portfolio_id:
            query = select(Portfolio).where(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == user_id,
            )
        else:
            query = select(Portfolio).where(
                Portfolio.user_id == user_id
            ).order_by(Portfolio.created_at.asc())

        result = await self.db.execute(query)
        portfolio = result.scalar_one_or_none()
        if not portfolio:
            raise ValueError("Portfolio not found")

        # Delete all positions
        result = await self.db.execute(
            select(Position).where(Position.portfolio_id == portfolio.id)
        )
        for position in result.scalars().all():
            await self.db.delete(position)

        # Reset balances
        portfolio.cash_balance = portfolio.initial_balance
        portfolio.reserved_balance = 0.0

        await self.db.flush()
        logger.info(f"Portfolio {portfolio.id} reset for user {user_id}")

        return await self.get_summary(user_id, portfolio.id)
