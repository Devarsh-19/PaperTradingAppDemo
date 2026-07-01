"""
Intelligence Service — FastAPI application for analytics, screening, and indicators.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import get_settings
from app.api.v1.screener import router as screener_router
from app.api.v1.indicators import router as indicators_router
from app.api.v1.performance import router as performance_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    logger.info("Shutting down Intelligence Service")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Stock screening, technical indicators, and portfolio analytics.",
    docs_url="/intelligence/docs",
    redoc_url="/intelligence/redoc",
    openapi_url="/intelligence/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
PREFIX = "/intelligence/v1"
app.include_router(screener_router, prefix=PREFIX)
app.include_router(indicators_router, prefix=PREFIX)
app.include_router(performance_router, prefix=PREFIX)


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }
