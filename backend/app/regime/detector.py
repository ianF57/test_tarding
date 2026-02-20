from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


def _adx(df: pd.DataFrame, n: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    plus_dm = (high.diff()).clip(lower=0)
    minus_dm = (-low.diff()).clip(lower=0)
    tr = pd.concat([(high - low), (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(n).mean()
    plus_di = 100 * (plus_dm.rolling(n).mean() / atr.replace(0, np.nan))
    minus_di = 100 * (minus_dm.rolling(n).mean() / atr.replace(0, np.nan))
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)).fillna(0)
    return dx.rolling(n).mean().fillna(0)


def detect_regime(df: pd.DataFrame) -> str:
    close = df["close"].astype(float)
    ret = close.pct_change().fillna(0)
    rolling_vol = ret.rolling(24).std().fillna(ret.std())
    adx = _adx(df).fillna(0)

    features = pd.DataFrame({"vol": rolling_vol, "trend": adx}).dropna()
    if len(features) < 20:
        return "unknown"

    model = KMeans(n_clusters=4, random_state=42, n_init="auto")
    labels = model.fit_predict(features)
    latest_cluster = labels[-1]
    center = model.cluster_centers_[latest_cluster]
    vol_level, trend_level = center[0], center[1]

    if trend_level >= np.quantile(model.cluster_centers_[:, 1], 0.6):
        return "trending_high_vol" if vol_level >= np.quantile(model.cluster_centers_[:, 0], 0.6) else "trending_low_vol"
    return "ranging_high_vol" if vol_level >= np.quantile(model.cluster_centers_[:, 0], 0.6) else "ranging_low_vol"
