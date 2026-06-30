"""Technical indicators endpoint."""

from fastapi import APIRouter, HTTPException

from app.schemas.indicators import IndicatorsResponse
from app.services.indicator_service import IndicatorService

router = APIRouter(tags=["Indicators"])


@router.get(
    "/indicators/{symbol}",
    response_model=IndicatorsResponse,
    summary="Get technical indicators for a symbol",
)
async def get_indicators(symbol: str):
    """
    Calculate technical indicators for a stock symbol.
    
    Returns: SMA (20, 50, 200), EMA (12, 26, 50), RSI (14),
    MACD (12, 26, 9), ATR (14), and 20-day volume average.
    """
    service = IndicatorService()
    try:
        return await service.get_indicators(symbol)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
