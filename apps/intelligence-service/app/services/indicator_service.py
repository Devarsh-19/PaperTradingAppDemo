"""
Technical indicator service — calculates SMA, EMA, RSI, MACD from price data.
"""

import numpy as np
import pandas as pd
import yfinance as yf
from loguru import logger

from app.schemas.indicators import IndicatorsResponse, MACDResult, MovingAverage


class IndicatorService:
    """Calculates technical indicators from Yahoo Finance historical data."""

    async def get_indicators(self, symbol: str) -> IndicatorsResponse:
        symbol = symbol.upper().strip()
        logger.info(f"Calculating indicators for {symbol}")

        ticker = yf.Ticker(symbol)
        df = ticker.history(period="6mo", interval="1d")

        if df.empty:
            raise ValueError(f"No data available for '{symbol}'")

        close = df["Close"]
        volume = df["Volume"]
        high = df["High"]
        low = df["Low"]
        current_price = float(close.iloc[-1])

        # ── SMA ──
        sma_periods = [20, 50, 200]
        sma_values = []
        for period in sma_periods:
            val = float(close.rolling(window=period).mean().iloc[-1]) if len(close) >= period else None
            sma_values.append(MovingAverage(period=period, value=round(val, 4) if val else None))

        # ── EMA ──
        ema_periods = [12, 26, 50]
        ema_values = []
        for period in ema_periods:
            val = float(close.ewm(span=period, adjust=False).mean().iloc[-1]) if len(close) >= period else None
            ema_values.append(MovingAverage(period=period, value=round(val, 4) if val else None))

        # ── RSI (14) ──
        rsi_14 = self._calculate_rsi(close, 14)

        # ── MACD (12, 26, 9) ──
        macd = self._calculate_macd(close)

        # ── ATR (14) ──
        atr_14 = self._calculate_atr(high, low, close, 14)

        # ── Volume Average (20-day) ──
        vol_avg = int(volume.rolling(window=20).mean().iloc[-1]) if len(volume) >= 20 else None

        return IndicatorsResponse(
            symbol=symbol,
            price=round(current_price, 4),
            sma=sma_values,
            ema=ema_values,
            rsi_14=rsi_14,
            macd=macd,
            atr_14=atr_14,
            volume_avg_20=vol_avg,
        )

    def _calculate_rsi(self, close: pd.Series, period: int = 14) -> float | None:
        """Calculate Relative Strength Index."""
        if len(close) < period + 1:
            return None

        delta = close.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))

        val = float(rsi.iloc[-1])
        return round(val, 2) if not np.isnan(val) else None

    def _calculate_macd(
        self, close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> MACDResult | None:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        if len(close) < slow + signal:
            return None

        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return MACDResult(
            macd_line=round(float(macd_line.iloc[-1]), 4),
            signal_line=round(float(signal_line.iloc[-1]), 4),
            histogram=round(float(histogram.iloc[-1]), 4),
        )

    def _calculate_atr(
        self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
    ) -> float | None:
        """Calculate Average True Range."""
        if len(close) < period + 1:
            return None

        prev_close = close.shift(1)
        tr = pd.concat([
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ], axis=1).max(axis=1)

        atr = tr.rolling(window=period).mean()
        val = float(atr.iloc[-1])
        return round(val, 4) if not np.isnan(val) else None
