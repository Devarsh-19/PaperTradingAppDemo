"""
Order service — orchestrates order placement, validation, and cancellation.

Delegates actual execution to the MatchingEngine.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderSide, OrderStatus, OrderType
from app.models.portfolio import Portfolio
from app.models.position import Position
from app.schemas.order import OrderCreateRequest, OrderListResponse, OrderResponse
from app.services.market_data_service import MarketDataService
from app.services.matching_engine import MatchingEngine


class OrderService:
    """Orchestrates order placement, validation, and lifecycle management."""

    def __init__(
        self,
        db: AsyncSession,
        market_data: MarketDataService,
    ):
        self.db = db
        self.market_data = market_data
        self.engine = MatchingEngine(db)

    async def place_order(
        self,
        user_id: uuid.UUID,
        portfolio_id: uuid.UUID,
        data: OrderCreateRequest,
    ) -> OrderResponse:
        """
        Place a new order.

        1. Validate the order (funds, shares, symbol)
        2. Create the order record
        3. For MARKET orders: execute immediately
        4. For LIMIT/STOP orders: set status to OPEN and reserve funds
        """
        symbol = data.symbol.upper().strip()

        # Fetch current price
        current_price = await self.market_data.get_current_price(symbol)

        # Fetch portfolio
        result = await self.db.execute(
            select(Portfolio).where(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == user_id,
            )
        )
        portfolio = result.scalar_one_or_none()
        if not portfolio:
            raise ValueError("Portfolio not found")

        # Create order record
        order = Order(
            user_id=user_id,
            portfolio_id=portfolio_id,
            symbol=symbol,
            order_type=data.order_type,
            side=data.side,
            quantity=data.quantity,
            price=current_price,
            limit_price=data.limit_price,
            stop_price=data.stop_price,
            status=OrderStatus.PENDING,
        )
        self.db.add(order)
        await self.db.flush()

        # ── Pre-validation ──
        if data.side == OrderSide.BUY:
            required = data.quantity * (
                data.limit_price or data.stop_price or current_price
            )
            if portfolio.available_cash < required:
                order.status = OrderStatus.REJECTED
                order.reject_reason = (
                    f"Insufficient funds: need ${required:.2f}, "
                    f"available ${portfolio.available_cash:.2f}"
                )
                await self.db.flush()
                return OrderResponse.model_validate(order)

        elif data.side == OrderSide.SELL:
            result = await self.db.execute(
                select(Position).where(
                    Position.portfolio_id == portfolio_id,
                    Position.symbol == symbol,
                )
            )
            position = result.scalar_one_or_none()
            if not position or position.quantity < data.quantity:
                available = position.quantity if position else 0
                order.status = OrderStatus.REJECTED
                order.reject_reason = (
                    f"Insufficient shares: need {data.quantity}, "
                    f"available {available}"
                )
                await self.db.flush()
                return OrderResponse.model_validate(order)

        # ── Execute based on order type ──
        try:
            if data.order_type == OrderType.MARKET:
                await self.engine.execute_market_order(order, current_price)

            elif data.order_type == OrderType.LIMIT:
                # Reserve funds for buy limit orders
                if data.side == OrderSide.BUY:
                    reserved = data.quantity * data.limit_price
                    portfolio.reserved_balance += reserved
                order.status = OrderStatus.OPEN
                logger.info(f"LIMIT order {order.id} placed — waiting for price condition")

            elif data.order_type == OrderType.STOP_LOSS:
                order.status = OrderStatus.OPEN
                logger.info(f"STOP_LOSS order {order.id} placed — waiting for trigger")

        except ValueError as e:
            logger.warning(f"Order {order.id} rejected: {e}")

        await self.db.flush()
        return OrderResponse.model_validate(order)

    async def get_orders(
        self,
        user_id: uuid.UUID,
        status_filter: Optional[OrderStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> OrderListResponse:
        """Get paginated list of orders for a user."""
        query = select(Order).where(Order.user_id == user_id)
        count_query = select(func.count()).select_from(Order).where(Order.user_id == user_id)

        if status_filter:
            query = query.where(Order.status == status_filter)
            count_query = count_query.where(Order.status == status_filter)

        # Total count
        total = (await self.db.execute(count_query)).scalar()

        # Paginated results
        query = (
            query
            .order_by(Order.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.execute(query)
        orders = result.scalars().all()

        return OrderListResponse(
            orders=[OrderResponse.model_validate(o) for o in orders],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_order(self, user_id: uuid.UUID, order_id: uuid.UUID) -> OrderResponse:
        """Get a single order by ID."""
        result = await self.db.execute(
            select(Order).where(
                Order.id == order_id,
                Order.user_id == user_id,
            )
        )
        order = result.scalar_one_or_none()
        if not order:
            raise ValueError("Order not found")
        return OrderResponse.model_validate(order)

    async def cancel_order(self, user_id: uuid.UUID, order_id: uuid.UUID) -> OrderResponse:
        """
        Cancel a pending/open order.

        Releases any reserved funds for limit buy orders.
        """
        result = await self.db.execute(
            select(Order).where(
                Order.id == order_id,
                Order.user_id == user_id,
            )
        )
        order = result.scalar_one_or_none()
        if not order:
            raise ValueError("Order not found")

        if order.status not in (OrderStatus.PENDING, OrderStatus.OPEN):
            raise ValueError(
                f"Cannot cancel order with status {order.status.value}"
            )

        # Release reserved funds for buy limit orders
        if (
            order.order_type == OrderType.LIMIT
            and order.side == OrderSide.BUY
            and order.limit_price
        ):
            result = await self.db.execute(
                select(Portfolio).where(Portfolio.id == order.portfolio_id)
            )
            portfolio = result.scalar_one()
            reserved = order.quantity * order.limit_price
            portfolio.reserved_balance = max(0, portfolio.reserved_balance - reserved)

        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.now(timezone.utc)

        await self.db.flush()
        logger.info(f"Order {order.id} cancelled")

        return OrderResponse.model_validate(order)
