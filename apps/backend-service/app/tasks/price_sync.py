"""
Background task: Sync prices for all subscribed symbols and push updates
to connected WebSocket clients.
"""

from loguru import logger

from app.core.redis import get_redis
from app.services.market_data_service import MarketDataService
from app.websocket.manager import manager


async def sync_prices():
    """
    Fetch current prices for all symbols with active WebSocket subscribers
    and broadcast updates to connected clients.

    This task runs on a schedule (every 10-15 seconds) via APScheduler.
    """
    symbols = manager.subscribed_symbols

    if not symbols:
        return

    logger.debug(f"Price sync: fetching {len(symbols)} symbols: {symbols}")

    market_data = MarketDataService(redis=get_redis())

    for symbol in symbols:
        try:
            quote = await market_data.get_quote(symbol)
            await manager.broadcast_price_update(
                symbol,
                {
                    "symbol": quote.symbol,
                    "price": quote.price,
                    "change": quote.change,
                    "change_percent": quote.change_percent,
                    "volume": quote.volume,
                    "day_high": quote.day_high,
                    "day_low": quote.day_low,
                    "timestamp": quote.timestamp.isoformat() if quote.timestamp else None,
                },
            )
        except Exception as e:
            logger.error(f"Price sync failed for {symbol}: {e}")

    logger.debug(f"Price sync complete: {len(symbols)} symbols broadcast to {manager.connection_count} clients")
