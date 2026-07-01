"""
Performance analytics service — calculates trading performance metrics.

Fetches trade data from the trading service to compute win rate, 
average P&L, Sharpe ratio, etc.
"""

from typing import Optional
from pydantic import BaseModel

import httpx
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


class PerformanceMetrics(BaseModel):
    """Trading performance metrics for a user."""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    avg_profit: Optional[float] = None
    avg_loss: Optional[float] = None
    largest_win: Optional[float] = None
    largest_loss: Optional[float] = None
    profit_factor: Optional[float] = None


class PerformanceService:
    """Calculates trading performance from trade history."""

    async def get_performance(self, token: str) -> PerformanceMetrics:
        """
        Fetch trade history from the trading service and compute metrics.
        
        Args:
            token: JWT token to authenticate with the trading service.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.trading_service_url}/api/v1/portfolio/trades",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0,
                )

                if response.status_code != 200:
                    logger.warning(f"Could not fetch trades: {response.status_code}")
                    return PerformanceMetrics()

                trades = response.json()

        except Exception as e:
            logger.error(f"Error fetching trades from trading service: {e}")
            return PerformanceMetrics()

        if not trades:
            return PerformanceMetrics()

        # Pair buy/sell trades to compute P&L per round-trip
        # Simplified: compute P&L per sell trade vs average buy cost
        profits = []
        losses = []

        buy_costs: dict[str, list[float]] = {}  # symbol -> list of buy prices

        for trade in trades:
            symbol = trade.get("symbol", "")
            side = trade.get("side", "")
            price = trade.get("execution_price", 0)
            qty = trade.get("quantity", 0)

            if side == "BUY":
                buy_costs.setdefault(symbol, []).extend([price] * qty)
            elif side == "SELL" and symbol in buy_costs and buy_costs[symbol]:
                for _ in range(min(qty, len(buy_costs[symbol]))):
                    buy_price = buy_costs[symbol].pop(0)
                    pnl = (price - buy_price)
                    if pnl >= 0:
                        profits.append(pnl)
                    else:
                        losses.append(pnl)

        total = len(profits) + len(losses)
        if total == 0:
            return PerformanceMetrics(total_trades=len(trades))

        total_pnl = sum(profits) + sum(losses)
        avg_profit = sum(profits) / len(profits) if profits else None
        avg_loss = sum(losses) / len(losses) if losses else None
        total_loss = abs(sum(losses)) if losses else 0
        profit_factor = sum(profits) / total_loss if total_loss > 0 else None

        return PerformanceMetrics(
            total_trades=len(trades),
            winning_trades=len(profits),
            losing_trades=len(losses),
            win_rate=round(len(profits) / total * 100, 2),
            total_pnl=round(total_pnl, 2),
            avg_profit=round(avg_profit, 2) if avg_profit is not None else None,
            avg_loss=round(avg_loss, 2) if avg_loss is not None else None,
            largest_win=round(max(profits), 2) if profits else None,
            largest_loss=round(min(losses), 2) if losses else None,
            profit_factor=round(profit_factor, 2) if profit_factor is not None else None,
        )
