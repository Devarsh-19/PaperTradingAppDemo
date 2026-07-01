"""
Background task: Match open limit and stop-loss orders against current prices.

Runs on a schedule (every 15 seconds) to check if any pending orders
should be filled based on current market prices.
"""

from loguru import logger
from sqlalchemy import select

from app.core.database import async_session_factory
from app.core.redis import get_redis
from app.models.order import Order, OrderStatus, OrderType
from app.services.market_data_service import MarketDataService
from app.services.matching_engine import MatchingEngine
from app.websocket.manager import manager


async def match_open_orders():
    """
    Check all OPEN limit and stop-loss orders against current prices.

    For each open order:
    - LIMIT BUY: fill if current_price ≤ limit_price
    - LIMIT SELL: fill if current_price ≥ limit_price
    - STOP_LOSS SELL: fill if current_price ≤ stop_price
    - STOP_LOSS BUY: fill if current_price ≥ stop_price
    """
    async with async_session_factory() as db:
        try:
            # Fetch all open orders
            result = await db.execute(
                select(Order).where(Order.status == OrderStatus.OPEN)
            )
            open_orders = result.scalars().all()

            if not open_orders:
                return

            logger.info(f"Order matcher: checking {len(open_orders)} open orders")

            market_data = MarketDataService(redis=get_redis())
            engine = MatchingEngine(db)

            # Group by symbol to minimize API calls
            symbols = set(o.symbol for o in open_orders)
            price_map = {}
            for symbol in symbols:
                try:
                    price = await market_data.get_current_price(symbol)
                    price_map[symbol] = price
                except Exception as e:
                    logger.error(f"Failed to get price for {symbol}: {e}")

            filled_count = 0
            for order in open_orders:
                current_price = price_map.get(order.symbol)
                if current_price is None:
                    continue

                trade = None
                try:
                    if order.order_type == OrderType.LIMIT:
                        trade = await engine.execute_limit_order(order, current_price)
                    elif order.order_type == OrderType.STOP_LOSS:
                        trade = await engine.execute_stop_loss(order, current_price)
                except ValueError as e:
                    logger.warning(f"Order {order.id} execution failed: {e}")

                if trade:
                    filled_count += 1
                    # Notify user via WebSocket
                    await manager.send_to_user(
                        str(order.user_id),
                        "order_filled",
                        {
                            "order_id": str(order.id),
                            "symbol": order.symbol,
                            "side": order.side.value,
                            "quantity": trade.quantity,
                            "execution_price": trade.execution_price,
                            "total_value": trade.total_value,
                        },
                    )

            await db.commit()

            if filled_count:
                logger.info(f"Order matcher: filled {filled_count} orders")

        except Exception as e:
            logger.error(f"Order matcher error: {e}")
            await db.rollback()
