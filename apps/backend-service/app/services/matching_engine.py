"""
Matching engine — simulates order execution against live market prices.

Handles market orders (immediate fill), limit orders (fill when price
condition is met), and stop-loss orders (trigger market order at stop price).
"""

import uuid
from datetime import datetime, timezone

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderSide, OrderStatus, OrderType
from app.models.portfolio import Portfolio
from app.models.position import Position
from app.models.trade import Trade


class MatchingEngine:
    """Simulated order matching engine for paper trading."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_market_order(
        self,
        order: Order,
        current_price: float,
    ) -> Trade:
        """
        Execute a market order immediately at the current price.

        Steps:
          1. Calculate total value
          2. Update portfolio cash balance
          3. Update or create position
          4. Record the trade
          5. Update order status to FILLED
        """
        total_value = order.quantity * current_price
        logger.info(
            f"Executing MARKET {order.side.value} order: "
            f"{order.quantity} × {order.symbol} @ ${current_price:.2f} = ${total_value:.2f}"
        )

        # Fetch portfolio
        result = await self.db.execute(
            select(Portfolio).where(Portfolio.id == order.portfolio_id)
        )
        portfolio = result.scalar_one()

        if order.side == OrderSide.BUY:
            await self._execute_buy(portfolio, order, current_price, total_value)
        else:
            await self._execute_sell(portfolio, order, current_price, total_value)

        # Create trade record
        trade = Trade(
            order_id=order.id,
            user_id=order.user_id,
            symbol=order.symbol,
            side=order.side.value,
            quantity=order.quantity,
            execution_price=current_price,
            total_value=total_value,
        )
        self.db.add(trade)

        # Update order
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.price = current_price
        order.filled_at = datetime.now(timezone.utc)

        await self.db.flush()
        logger.info(f"Order {order.id} FILLED — Trade {trade.id} created")

        return trade

    async def execute_limit_order(
        self,
        order: Order,
        current_price: float,
    ) -> Trade | None:
        """
        Check if a limit order's condition is met, and execute if so.

        BUY LIMIT: executes when current_price ≤ limit_price
        SELL LIMIT: executes when current_price ≥ limit_price

        Returns the trade if executed, None otherwise.
        """
        should_fill = False

        if order.side == OrderSide.BUY and current_price <= order.limit_price:
            should_fill = True
        elif order.side == OrderSide.SELL and current_price >= order.limit_price:
            should_fill = True

        if not should_fill:
            return None

        logger.info(
            f"LIMIT {order.side.value} condition met for {order.symbol}: "
            f"price ${current_price:.2f} vs limit ${order.limit_price:.2f}"
        )

        # For limit orders, release reserved balance first
        result = await self.db.execute(
            select(Portfolio).where(Portfolio.id == order.portfolio_id)
        )
        portfolio = result.scalar_one()

        if order.side == OrderSide.BUY:
            # Release reserved funds
            reserved_amount = order.quantity * order.limit_price
            portfolio.reserved_balance -= reserved_amount

        # Execute at the current price (better than or equal to limit)
        return await self.execute_market_order(order, current_price)

    async def execute_stop_loss(
        self,
        order: Order,
        current_price: float,
    ) -> Trade | None:
        """
        Check if a stop-loss condition is met.

        SELL STOP-LOSS: triggers when current_price ≤ stop_price
        BUY STOP-LOSS: triggers when current_price ≥ stop_price

        Returns the trade if executed, None otherwise.
        """
        should_trigger = False

        if order.side == OrderSide.SELL and current_price <= order.stop_price:
            should_trigger = True
        elif order.side == OrderSide.BUY and current_price >= order.stop_price:
            should_trigger = True

        if not should_trigger:
            return None

        logger.info(
            f"STOP_LOSS triggered for {order.symbol}: "
            f"price ${current_price:.2f} hit stop ${order.stop_price:.2f}"
        )

        return await self.execute_market_order(order, current_price)

    async def _execute_buy(
        self,
        portfolio: Portfolio,
        order: Order,
        price: float,
        total_value: float,
    ) -> None:
        """Process a BUY: deduct cash, update/create position."""
        if portfolio.available_cash < total_value:
            order.status = OrderStatus.REJECTED
            order.reject_reason = (
                f"Insufficient funds: need ${total_value:.2f}, "
                f"available ${portfolio.available_cash:.2f}"
            )
            raise ValueError(order.reject_reason)

        # Deduct cash
        portfolio.cash_balance -= total_value

        # Update or create position
        result = await self.db.execute(
            select(Position).where(
                Position.portfolio_id == portfolio.id,
                Position.symbol == order.symbol,
            )
        )
        position = result.scalar_one_or_none()

        if position:
            # Update avg buy price: weighted average
            total_cost = (position.avg_buy_price * position.quantity) + total_value
            position.quantity += order.quantity
            position.avg_buy_price = total_cost / position.quantity
            position.total_invested = total_cost
        else:
            position = Position(
                portfolio_id=portfolio.id,
                symbol=order.symbol,
                quantity=order.quantity,
                avg_buy_price=price,
                total_invested=total_value,
            )
            self.db.add(position)

    async def _execute_sell(
        self,
        portfolio: Portfolio,
        order: Order,
        price: float,
        total_value: float,
    ) -> None:
        """Process a SELL: add cash, reduce/close position."""
        # Check position exists with enough shares
        result = await self.db.execute(
            select(Position).where(
                Position.portfolio_id == portfolio.id,
                Position.symbol == order.symbol,
            )
        )
        position = result.scalar_one_or_none()

        if not position or position.quantity < order.quantity:
            order.status = OrderStatus.REJECTED
            available = position.quantity if position else 0
            order.reject_reason = (
                f"Insufficient shares: need {order.quantity}, "
                f"available {available}"
            )
            raise ValueError(order.reject_reason)

        # Add cash
        portfolio.cash_balance += total_value

        # Reduce position
        position.quantity -= order.quantity
        cost_removed = order.quantity * position.avg_buy_price
        position.total_invested -= cost_removed

        # Remove position if fully sold
        if position.quantity == 0:
            await self.db.delete(position)
