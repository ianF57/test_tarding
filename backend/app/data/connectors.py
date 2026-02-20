from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import httpx
import numpy as np
import pandas as pd


@dataclass
class BaseConnector:
    name: str

    async def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 500) -> pd.DataFrame:
        raise NotImplementedError


class BinanceConnector(BaseConnector):
    def __init__(self) -> None:
        super().__init__(name="binance")

    async def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 500) -> pd.DataFrame:
        interval_map = {"1m": "1m", "5m": "5m", "1h": "1h", "1d": "1d", "1w": "1w"}
        interval = interval_map.get(timeframe, "1h")
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": min(limit, 1000)}
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            rows = r.json()

        df = pd.DataFrame(
            rows,
            columns=[
                "open_time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_asset_volume",
                "number_of_trades",
                "taker_buy_base_asset_volume",
                "taker_buy_quote_asset_volume",
                "ignore",
            ],
        )
        df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        return df[["timestamp", "open", "high", "low", "close", "volume"]].dropna()


class SyntheticConnector(BaseConnector):
    """Fallback connector for forex/futures when APIs are not configured."""

    def __init__(self, name: str) -> None:
        super().__init__(name=name)

    async def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 500) -> pd.DataFrame:
        np.random.seed(abs(hash((self.name, symbol, timeframe))) % 2**32)
        freq = {"1m": "1min", "5m": "5min", "1h": "1h", "1d": "1D", "1w": "1W"}.get(timeframe, "1h")
        end = datetime.now(timezone.utc)
        idx = pd.date_range(end=end, periods=limit, freq=freq)
        noise = np.random.normal(0, 0.003, limit)
        trend = np.linspace(-0.03, 0.03, limit)
        returns = noise + trend / limit
        close = 100 * (1 + pd.Series(returns)).cumprod()
        high = close * (1 + np.random.uniform(0, 0.005, limit))
        low = close * (1 - np.random.uniform(0, 0.005, limit))
        open_ = close.shift(1).fillna(close.iloc[0])
        volume = np.random.randint(100, 1000, limit)
        return pd.DataFrame(
            {
                "timestamp": idx,
                "open": open_.values,
                "high": high.values,
                "low": low.values,
                "close": close.values,
                "volume": volume,
            }
        )


def get_connector(market: str) -> BaseConnector:
    if market == "crypto":
        return BinanceConnector()
    if market == "forex":
        return SyntheticConnector("oanda")
    return SyntheticConnector("cme")
