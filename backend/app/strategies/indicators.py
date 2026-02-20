from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window).mean()


def ema(series: pd.Series, window: int) -> pd.Series:
    return series.ewm(span=window, adjust=False).mean()


def macd(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    macd_line = ema(series, 12) - ema(series, 26)
    signal = ema(macd_line, 9)
    return macd_line, signal


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    diff = series.diff()
    up = diff.clip(lower=0).rolling(window).mean()
    down = -diff.clip(upper=0).rolling(window).mean()
    rs = up / down.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def stochastic(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    ll = low.rolling(window).min()
    hh = high.rolling(window).max()
    return 100 * ((close - ll) / (hh - ll).replace(0, np.nan))


def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    tr = pd.concat(
        [(high - low), (high - close.shift()).abs(), (low - close.shift()).abs()],
        axis=1,
    ).max(axis=1)
    return tr.rolling(window).mean()


def bollinger(close: pd.Series, window: int = 20, n_std: float = 2) -> tuple[pd.Series, pd.Series]:
    mid = close.rolling(window).mean()
    std = close.rolling(window).std()
    return mid + n_std * std, mid - n_std * std


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    signed_volume = np.sign(close.diff().fillna(0)) * volume.fillna(0)
    return signed_volume.cumsum()
