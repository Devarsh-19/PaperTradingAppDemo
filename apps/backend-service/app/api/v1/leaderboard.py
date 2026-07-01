"""
Leaderboard routes — global ranking and user's own rank.
"""

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DbSession
from app.core.redis import get_redis
from app.services.leaderboard_service import (
    LeaderboardEntry,
    LeaderboardResponse,
    LeaderboardService,
)
from app.services.market_data_service import MarketDataService

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


def _get_leaderboard_service(db) -> LeaderboardService:
    market_data = MarketDataService(redis=get_redis())
    return LeaderboardService(db, market_data)


@router.get(
    "",
    response_model=LeaderboardResponse,
    summary="Global leaderboard",
)
async def get_leaderboard(
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(50, ge=1, le=100),
):
    """
    Get the global leaderboard ranked by total portfolio value.

    Returns usernames, total values, P&L, and rankings.
    """
    service = _get_leaderboard_service(db)
    return await service.get_leaderboard(limit=limit)


@router.get(
    "/me",
    response_model=LeaderboardEntry,
    summary="My ranking",
)
async def get_my_rank(current_user: CurrentUser, db: DbSession):
    """Get the current user's rank on the leaderboard."""
    service = _get_leaderboard_service(db)
    entry = await service.get_user_rank(current_user.id)
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not on the leaderboard yet",
        )
    return entry
