"""
Portfolio routes — summary, positions, trades, and reset.
"""

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.portfolio import (
    PortfolioSummaryResponse,
    PositionResponse,
    TradeListResponse,
)
from app.services.market_data_service import MarketDataService
from app.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


def _get_portfolio_service(db) -> PortfolioService:
    market_data = MarketDataService(redis=None)
    return PortfolioService(db, market_data)


@router.get(
    "/summary",
    response_model=PortfolioSummaryResponse,
    summary="Portfolio overview with P&L",
)
async def get_summary(current_user: CurrentUser, db: DbSession):
    """
    Get a high-level portfolio overview including:
    - Cash balance & available cash
    - Total invested value vs. current market value
    - Unrealized P&L (absolute and percentage)
    - Number of open positions
    """
    try:
        service = _get_portfolio_service(db)
        return await service.get_summary(current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/positions",
    response_model=list[PositionResponse],
    summary="List all holdings",
)
async def get_positions(current_user: CurrentUser, db: DbSession):
    """
    Get all current stock positions with live pricing and unrealized P&L.
    """
    try:
        service = _get_portfolio_service(db)
        return await service.get_positions(current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/trades",
    response_model=TradeListResponse,
    summary="Trade history",
)
async def get_trades(
    current_user: CurrentUser,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Get paginated history of all executed trades."""
    service = _get_portfolio_service(db)
    return await service.get_trades(
        current_user.id,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/reset",
    response_model=PortfolioSummaryResponse,
    summary="Reset portfolio to starting balance",
)
async def reset_portfolio(current_user: CurrentUser, db: DbSession):
    """
    Reset the portfolio back to the initial virtual balance.

    **Warning**: This deletes all positions and is irreversible.
    """
    try:
        service = _get_portfolio_service(db)
        return await service.reset_portfolio(current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
