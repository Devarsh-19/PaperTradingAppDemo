"""
Stock screener service — filters stocks by fundamental and technical criteria.
"""

import yfinance as yf
from loguru import logger

from app.schemas.screener import ScreenerFilter, ScreenerResult, ScreenerResponse


class ScreenerService:
    """Screens stocks against user-defined filters using Yahoo Finance data."""

    async def screen(self, filters: ScreenerFilter) -> ScreenerResponse:
        results = []
        filters_applied = 0

        # Count active filters
        for field in [
            "min_market_cap", "max_market_cap", "min_pe_ratio", "max_pe_ratio",
            "min_volume", "min_price", "max_price", "min_change_percent",
            "max_change_percent", "sector",
        ]:
            if getattr(filters, field) is not None:
                filters_applied += 1

        for symbol in filters.symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info

                price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
                prev_close = info.get("previousClose", 0)
                change = price - prev_close if price and prev_close else 0
                change_pct = (change / prev_close * 100) if prev_close else 0
                market_cap = info.get("marketCap")
                pe_ratio = info.get("trailingPE")
                volume = info.get("volume") or info.get("regularMarketVolume")
                sector = info.get("sector")

                # Apply filters
                if filters.min_market_cap and (not market_cap or market_cap < filters.min_market_cap):
                    continue
                if filters.max_market_cap and (market_cap and market_cap > filters.max_market_cap):
                    continue
                if filters.min_pe_ratio and (not pe_ratio or pe_ratio < filters.min_pe_ratio):
                    continue
                if filters.max_pe_ratio and (pe_ratio and pe_ratio > filters.max_pe_ratio):
                    continue
                if filters.min_volume and (not volume or volume < filters.min_volume):
                    continue
                if filters.min_price and price < filters.min_price:
                    continue
                if filters.max_price and price > filters.max_price:
                    continue
                if filters.min_change_percent and change_pct < filters.min_change_percent:
                    continue
                if filters.max_change_percent and change_pct > filters.max_change_percent:
                    continue
                if filters.sector and (not sector or sector.lower() != filters.sector.lower()):
                    continue

                results.append(ScreenerResult(
                    symbol=symbol,
                    name=info.get("shortName") or info.get("longName"),
                    price=round(price, 2),
                    change=round(change, 2),
                    change_percent=round(change_pct, 2),
                    volume=volume,
                    market_cap=market_cap,
                    pe_ratio=round(pe_ratio, 2) if pe_ratio else None,
                    sector=sector,
                ))
            except Exception as e:
                logger.warning(f"Screener skipping {symbol}: {e}")

        return ScreenerResponse(
            results=results,
            total=len(results),
            filters_applied=filters_applied,
        )
