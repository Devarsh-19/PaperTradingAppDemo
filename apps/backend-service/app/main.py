"""
Paper Trading App — FastAPI application factory.

Configures CORS, registers all routers, sets up background tasks,
and manages startup/shutdown lifecycle events.
"""

from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import get_settings
from app.core.database import engine
from app.core.redis import init_redis, close_redis

# ── Import routers ──
from app.api.v1.auth import router as auth_router
from app.api.v1.orders import router as orders_router
from app.api.v1.portfolio import router as portfolio_router
from app.api.v1.market import router as market_router
from app.api.v1.watchlist import router as watchlist_router
from app.api.v1.leaderboard import router as leaderboard_router

# ── Import WebSocket routers ──
from app.websocket.price_stream import router as ws_price_router
from app.websocket.order_updates import router as ws_order_router

# ── Import background tasks ──
from app.tasks.price_sync import sync_prices
from app.tasks.order_matcher import match_open_orders

settings = get_settings()

# ── Background Scheduler ──
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.

    Startup:
    - Start background task scheduler (price sync + order matcher)

    Shutdown:
    - Stop scheduler
    - Dispose database engine
    """
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"   Environment: {settings.environment}")
    logger.info(f"   Debug: {settings.debug}")

    # ── Connect Redis ──
    await init_redis()

    # ── Start background tasks ──
    scheduler.add_job(
        sync_prices,
        "interval",
        seconds=settings.price_sync_interval_seconds,
        id="price_sync",
        name="Price Sync",
    )
    scheduler.add_job(
        match_open_orders,
        "interval",
        seconds=settings.order_match_interval_seconds,
        id="order_matcher",
        name="Order Matcher",
    )
    scheduler.start()
    logger.info("📡 Background tasks started (price sync + order matcher)")

    yield  # ← App is running

    # ── Shutdown ──
    logger.info("Shutting down...")
    scheduler.shutdown(wait=False)
    await close_redis()
    await engine.dispose()
    logger.info("✅ Shutdown complete")


# ── Create App ──
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A paper trading API that lets you simulate stock trading "
        "with virtual money. Place market, limit, and stop-loss orders, "
        "track your portfolio P&L, and compete on the leaderboard."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register REST Routers ──
API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(orders_router, prefix=API_PREFIX)
app.include_router(portfolio_router, prefix=API_PREFIX)
app.include_router(market_router, prefix=API_PREFIX)
app.include_router(watchlist_router, prefix=API_PREFIX)
app.include_router(leaderboard_router, prefix=API_PREFIX)

# ── Register WebSocket Routers ──
app.include_router(ws_price_router)
app.include_router(ws_order_router)


# ── Health Check ──
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }