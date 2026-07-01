"""
Order routes — place, list, get, and cancel orders.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DbSession
from app.core.redis import get_redis
from app.models.order import OrderStatus
from app.schemas.order import OrderCreateRequest, OrderListResponse, OrderResponse
from app.services.market_data_service import MarketDataService
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


def _get_order_service(db) -> OrderService:
    """Create an OrderService with a MarketDataService."""
    market_data = MarketDataService(redis=get_redis())
    return OrderService(db, market_data)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Place a new order",
)
async def place_order(
    data: OrderCreateRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Place a buy or sell order.

    - **MARKET**: Executes immediately at current price.
    - **LIMIT**: Waits until price reaches the limit_price.
    - **STOP_LOSS**: Triggers when price drops to stop_price.
    """
    try:
        service = _get_order_service(db)
        # Use the first portfolio (default)
        if not current_user.portfolios:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No portfolio found — please contact support",
            )
        portfolio_id = current_user.portfolios[0].id
        return await service.place_order(current_user.id, portfolio_id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=OrderListResponse,
    summary="List your orders",
)
async def list_orders(
    current_user: CurrentUser,
    db: DbSession,
    status_filter: Optional[OrderStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Get a paginated list of your orders, optionally filtered by status."""
    service = _get_order_service(db)
    return await service.get_orders(
        current_user.id,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order details",
)
async def get_order(
    order_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """Get details for a specific order."""
    try:
        service = _get_order_service(db)
        return await service.get_order(current_user.id, order_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    summary="Cancel a pending order",
)
async def cancel_order(
    order_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Cancel a pending or open order.

    Reserved funds for limit buy orders are released back to cash.
    """
    try:
        service = _get_order_service(db)
        return await service.cancel_order(current_user.id, order_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
