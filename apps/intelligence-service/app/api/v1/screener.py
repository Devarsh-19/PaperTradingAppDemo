"""Stock screener endpoint."""

from fastapi import APIRouter

from app.schemas.screener import ScreenerFilter, ScreenerResponse
from app.services.screener_service import ScreenerService

router = APIRouter(tags=["Screener"])


@router.post("/screener", response_model=ScreenerResponse, summary="Screen stocks with filters")
async def screen_stocks(filters: ScreenerFilter = ScreenerFilter()):
    """
    Screen stocks against fundamental and technical criteria.
    
    Filters include market cap, P/E ratio, volume, price range,
    percent change, and sector. Defaults to screening the top 25 US stocks.
    """
    service = ScreenerService()
    return await service.screen(filters)
