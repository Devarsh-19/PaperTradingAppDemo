"""
Watchlist routes — create, list, add/remove symbols.
"""

import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DbSession
from app.models.watchlist import Watchlist, WatchlistItem
from app.schemas.watchlist import (
    WatchlistAddSymbolRequest,
    WatchlistCreateRequest,
    WatchlistResponse,
)

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


@router.get(
    "",
    response_model=list[WatchlistResponse],
    summary="Get all watchlists",
)
async def get_watchlists(current_user: CurrentUser, db: DbSession):
    """Get all watchlists for the current user with their items."""
    result = await db.execute(
        select(Watchlist)
        .where(Watchlist.user_id == current_user.id)
        .order_by(Watchlist.created_at.asc())
    )
    watchlists = result.scalars().all()
    return [WatchlistResponse.model_validate(w) for w in watchlists]


@router.post(
    "",
    response_model=WatchlistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new watchlist",
)
async def create_watchlist(
    data: WatchlistCreateRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Create a new empty watchlist."""
    watchlist = Watchlist(
        user_id=current_user.id,
        name=data.name,
    )
    db.add(watchlist)
    await db.flush()
    return WatchlistResponse.model_validate(watchlist)


@router.post(
    "/{watchlist_id}/symbols",
    response_model=WatchlistResponse,
    summary="Add a symbol to a watchlist",
)
async def add_symbol(
    watchlist_id: uuid.UUID,
    data: WatchlistAddSymbolRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Add a stock symbol to a watchlist. Ignores duplicates."""
    # Verify ownership
    result = await db.execute(
        select(Watchlist).where(
            Watchlist.id == watchlist_id,
            Watchlist.user_id == current_user.id,
        )
    )
    watchlist = result.scalar_one_or_none()
    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found",
        )

    symbol = data.symbol.upper().strip()

    # Check for duplicate
    existing = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.watchlist_id == watchlist_id,
            WatchlistItem.symbol == symbol,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{symbol} is already in this watchlist",
        )

    item = WatchlistItem(
        watchlist_id=watchlist_id,
        symbol=symbol,
    )
    db.add(item)
    await db.flush()

    # Re-fetch with items
    await db.refresh(watchlist)
    return WatchlistResponse.model_validate(watchlist)


@router.delete(
    "/{watchlist_id}/symbols/{symbol}",
    response_model=WatchlistResponse,
    summary="Remove a symbol from a watchlist",
)
async def remove_symbol(
    watchlist_id: uuid.UUID,
    symbol: str,
    current_user: CurrentUser,
    db: DbSession,
):
    """Remove a stock symbol from a watchlist."""
    # Verify ownership
    result = await db.execute(
        select(Watchlist).where(
            Watchlist.id == watchlist_id,
            Watchlist.user_id == current_user.id,
        )
    )
    watchlist = result.scalar_one_or_none()
    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found",
        )

    symbol = symbol.upper().strip()

    result = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.watchlist_id == watchlist_id,
            WatchlistItem.symbol == symbol,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{symbol} not found in this watchlist",
        )

    await db.delete(item)
    await db.flush()

    await db.refresh(watchlist)
    return WatchlistResponse.model_validate(watchlist)


@router.delete(
    "/{watchlist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a watchlist",
)
async def delete_watchlist(
    watchlist_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """Delete a watchlist and all its items."""
    result = await db.execute(
        select(Watchlist).where(
            Watchlist.id == watchlist_id,
            Watchlist.user_id == current_user.id,
        )
    )
    watchlist = result.scalar_one_or_none()
    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found",
        )

    await db.delete(watchlist)
    await db.flush()
