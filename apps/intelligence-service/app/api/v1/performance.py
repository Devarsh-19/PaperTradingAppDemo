"""Performance analytics endpoint."""

from fastapi import APIRouter, Header, HTTPException

from app.services.performance_service import PerformanceMetrics, PerformanceService

router = APIRouter(tags=["Performance"])


@router.get(
    "/performance",
    response_model=PerformanceMetrics,
    summary="Get trading performance metrics",
)
async def get_performance(authorization: str = Header(...)):
    """
    Calculate trading performance metrics (win rate, P&L, profit factor).
    
    Fetches your trade history from the trading service and computes
    round-trip P&L statistics.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ", 1)[1]
    service = PerformanceService()
    return await service.get_performance(token)
