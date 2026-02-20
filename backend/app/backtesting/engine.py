from __future__ import annotations

import numpy as np
import pandas as pd


def _annualization_factor(timeframe: str) -> int:
    return {"1m": 525600, "5m": 105120, "1h": 8760, "1d": 252, "1w": 52}.get(timeframe, 252)


def backtest(df: pd.DataFrame, signal: pd.Series, timeframe: str, transaction_cost_bps: float, slippage_bps: float, position_size: float = 1.0) -> dict:
    prices = df["close"].astype(float)
    returns = prices.pct_change().fillna(0)
    shifted_signal = signal.shift(1).fillna(0)
    trades = shifted_signal.diff().abs().fillna(0)

    total_cost = (transaction_cost_bps + slippage_bps) / 10000
    strat_returns = shifted_signal * returns * position_size - trades * total_cost
    equity = (1 + strat_returns).cumprod()

    ann = _annualization_factor(timeframe)
    cagr = equity.iloc[-1] ** (ann / len(equity)) - 1 if len(equity) > 1 else 0.0
    vol = strat_returns.std() * np.sqrt(ann)
    downside = strat_returns[strat_returns < 0].std() * np.sqrt(ann)
    sharpe = ((strat_returns.mean() * ann) / vol) if vol and not np.isnan(vol) else 0.0
    sortino = ((strat_returns.mean() * ann) / downside) if downside and not np.isnan(downside) else 0.0

    rolling_max = equity.cummax()
    drawdown = equity / rolling_max - 1
    max_dd = drawdown.min() if len(drawdown) else 0.0

    wins = strat_returns[strat_returns > 0]
    losses = strat_returns[strat_returns < 0]
    win_rate = (len(wins) / max(len(wins) + len(losses), 1))
    profit_factor = (wins.sum() / abs(losses.sum())) if losses.sum() != 0 else float("inf")

    direction_score = signal.tail(20).mean()
    direction = "long" if direction_score > 0.2 else "short" if direction_score < -0.2 else "neutral"

    return {
        "cagr": float(cagr),
        "sharpe": float(sharpe),
        "sortino": float(sortino),
        "max_drawdown": float(max_dd),
        "win_rate": float(win_rate),
        "profit_factor": float(profit_factor if np.isfinite(profit_factor) else 10.0),
        "direction": direction,
        "equity": equity,
    }
