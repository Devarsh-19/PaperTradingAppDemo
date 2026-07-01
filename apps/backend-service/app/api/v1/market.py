"""
Market data routes — quotes, history, search, trending.
"""

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DbSession
from app.core.redis import get_redis
from app.schemas.market import (
    BatchQuoteRequest,
    HistoryResponse,
    QuoteResponse,
    SymbolSearchResult,
)
from app.services.market_data_service import MarketDataService

router = APIRouter(prefix="/market", tags=["Market Data"])


def _get_market_service() -> MarketDataService:
    return MarketDataService(redis=get_redis())


@router.get(
    "/quote/{symbol}",
    response_model=QuoteResponse,
    summary="Get a real-time quote",
)
async def get_quote(symbol: str, current_user: CurrentUser):
    """
    Fetch a real-time quote for a stock symbol.

    Returns current price, day change, volume, market cap, and more.
    """
    try:
        service = _get_market_service()
        return await service.get_quote(symbol)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/quotes",
    response_model=list[QuoteResponse],
    summary="Get batch quotes",
)
async def get_batch_quotes(data: BatchQuoteRequest, current_user: CurrentUser):
    """Fetch quotes for multiple symbols in a single request."""
    service = _get_market_service()
    return await service.get_batch_quotes(data.symbols)


@router.get(
    "/history/{symbol}",
    response_model=HistoryResponse,
    summary="Get historical OHLCV data",
)
async def get_history(
    symbol: str,
    current_user: CurrentUser,
    period: str = Query("1mo", description="1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max"),
    interval: str = Query("1d", description="1m, 5m, 15m, 1h, 1d, 1wk, 1mo"),
):
    """
    Get historical OHLCV candle data for charting.

    Use `period` to set the time range and `interval` for candle granularity.
    """
    try:
        service = _get_market_service()
        return await service.get_history(symbol, period=period, interval=interval)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/search",
    response_model=list[SymbolSearchResult],
    summary="Search for symbols",
)
async def search_symbols(
    q: str = Query(..., min_length=1, description="Search query"),
    current_user: CurrentUser = None,
):
    """
    Search for stock symbols by name or ticker.

    Returns up to 10 matching results with symbol, name, and exchange.
    """
    service = _get_market_service()
    return await service.search_symbols(q)
