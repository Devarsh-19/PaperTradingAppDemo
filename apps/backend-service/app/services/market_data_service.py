"""
Market data service — fetches live and historical prices via yfinance.

Prices are cached in Redis with a configurable TTL to avoid rate limits.
"""

import json
from datetime import datetime, timezone
from typing import Optional

import yfinance as yf
from loguru import logger
from redis.asyncio import Redis

from app.core.config import get_settings
from app.schemas.market import (
    CandleResponse,
    HistoryResponse,
    QuoteResponse,
    SymbolSearchResult,
)

settings = get_settings()


class MarketDataService:
    """Fetches and caches market data from Yahoo Finance."""

    def __init__(self, redis: Optional[Redis] = None):
        self.redis = redis
        self.cache_ttl = settings.price_cache_ttl_seconds

    async def get_quote(self, symbol: str) -> QuoteResponse:
        """
        Get a real-time quote for a symbol.

        Checks Redis cache first; on miss, fetches from Yahoo Finance
        and caches the result.
        """
        symbol = symbol.upper().strip()
        cache_key = f"quote:{symbol}"

        # Try cache
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for {symbol}")
                return QuoteResponse(**json.loads(cached))

        # Fetch from Yahoo Finance
        logger.info(f"Fetching quote for {symbol} from Yahoo Finance")
        ticker = yf.Ticker(symbol)

        try:
            info = ticker.info
        except Exception as e:
            logger.error(f"Failed to fetch quote for {symbol}: {e}")
            raise ValueError(f"Could not fetch data for symbol '{symbol}'")

        price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose", 0)
        change = price - prev_close if price and prev_close else 0
        change_pct = (change / prev_close * 100) if prev_close else 0

        quote = QuoteResponse(
            symbol=symbol,
            name=info.get("shortName") or info.get("longName"),
            price=price,
            previous_close=prev_close,
            open=info.get("open") or info.get("regularMarketOpen"),
            day_high=info.get("dayHigh") or info.get("regularMarketDayHigh"),
            day_low=info.get("dayLow") or info.get("regularMarketDayLow"),
            volume=info.get("volume") or info.get("regularMarketVolume"),
            change=round(change, 4),
            change_percent=round(change_pct, 4),
            market_cap=info.get("marketCap"),
            timestamp=datetime.now(timezone.utc),
        )

        # Cache the result
        if self.redis:
            await self.redis.setex(
                cache_key,
                self.cache_ttl,
                quote.model_dump_json(),
            )

        return quote

    async def get_batch_quotes(self, symbols: list[str]) -> list[QuoteResponse]:
        """Fetch quotes for multiple symbols."""
        quotes = []
        for symbol in symbols:
            try:
                quote = await self.get_quote(symbol)
                quotes.append(quote)
            except ValueError:
                logger.warning(f"Skipping invalid symbol: {symbol}")
        return quotes

    async def get_current_price(self, symbol: str) -> float:
        """
        Get just the current price for a symbol.
        Convenience method for the order execution engine.
        """
        quote = await self.get_quote(symbol)
        return quote.price

    async def get_history(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d",
    ) -> HistoryResponse:
        """
        Get historical OHLCV candle data for charting.

        Args:
            symbol: Stock ticker.
            period: Time range (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max).
            interval: Candle interval (1m, 5m, 15m, 1h, 1d, 1wk, 1mo).
        """
        symbol = symbol.upper().strip()
        cache_key = f"history:{symbol}:{period}:{interval}"

        # Try cache (longer TTL for historical data)
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                return HistoryResponse(**json.loads(cached))

        logger.info(f"Fetching history for {symbol} (period={period}, interval={interval})")
        ticker = yf.Ticker(symbol)

        try:
            df = ticker.history(period=period, interval=interval)
        except Exception as e:
            logger.error(f"Failed to fetch history for {symbol}: {e}")
            raise ValueError(f"Could not fetch history for '{symbol}'")

        if df.empty:
            raise ValueError(f"No historical data for '{symbol}'")

        candles = []
        for idx, row in df.iterrows():
            candles.append(
                CandleResponse(
                    timestamp=idx.to_pydatetime().replace(tzinfo=timezone.utc),
                    open=round(row["Open"], 4),
                    high=round(row["High"], 4),
                    low=round(row["Low"], 4),
                    close=round(row["Close"], 4),
                    volume=int(row["Volume"]),
                )
            )

        history = HistoryResponse(
            symbol=symbol,
            interval=interval,
            candles=candles,
        )

        # Cache historical data longer (5 minutes)
        if self.redis:
            await self.redis.setex(cache_key, 300, history.model_dump_json())

        return history

    async def search_symbols(self, query: str) -> list[SymbolSearchResult]:
        """
        Search for symbols matching a query string.

        Uses yfinance's search functionality.
        """
        if not query or len(query) < 1:
            return []

        try:
            search = yf.Search(query)
            results = []
            for item in (search.quotes or [])[:10]:
                results.append(
                    SymbolSearchResult(
                        symbol=item.get("symbol", ""),
                        name=item.get("shortname") or item.get("longname", ""),
                        exchange=item.get("exchange"),
                        type=item.get("quoteType"),
                    )
                )
            return results
        except Exception as e:
            logger.error(f"Symbol search failed for '{query}': {e}")
            return []
