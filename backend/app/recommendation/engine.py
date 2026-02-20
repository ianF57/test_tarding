from __future__ import annotations

import pandas as pd

from app.backtesting.engine import backtest
from app.core.config import settings
from app.schemas.models import StrategyPerformance
from app.strategies.generator import StrategySpec, generate_signals


REGIME_STYLE_MAP = {
    "trending_high_vol": ["swing", "intraday"],
    "trending_low_vol": ["swing", "intraday"],
    "ranging_high_vol": ["intraday", "swing"],
    "ranging_low_vol": ["intraday", "swing"],
    "unknown": ["swing", "intraday"],
}


def _confidence(metrics: dict, regime: str, strategy: StrategySpec) -> float:
    score = 50.0
    score += min(metrics["sharpe"] * 10, 20)
    score += min(metrics["profit_factor"] * 3, 15)
    score -= abs(metrics["max_drawdown"]) * 100
    if strategy.style == REGIME_STYLE_MAP.get(regime, ["swing"])[0]:
        score += 10
    return float(max(0, min(100, score)))


def recommend(df: pd.DataFrame, timeframe: str, regime: str, strategies: list[StrategySpec]) -> list[StrategyPerformance]:
    rows: list[StrategyPerformance] = []
    for spec in strategies:
        signal = generate_signals(df, spec)
        metrics = backtest(
            df,
            signal,
            timeframe=timeframe,
            transaction_cost_bps=settings.transaction_cost_bps,
            slippage_bps=settings.slippage_bps,
            position_size=1.0,
        )
        rows.append(
            StrategyPerformance(
                name=spec.name,
                expected_annualized_return=metrics["cagr"],
                max_drawdown=metrics["max_drawdown"],
                sharpe_ratio=metrics["sharpe"],
                sortino_ratio=metrics["sortino"],
                win_rate=metrics["win_rate"],
                profit_factor=metrics["profit_factor"],
                suggested_direction=metrics["direction"],
                confidence_score=_confidence(metrics, regime, spec),
                favorable_conditions=f"Best in {spec.style} setups during {regime.replace('_', ' ')}",
            )
        )

    ranked = sorted(rows, key=lambda x: (x.confidence_score, x.sharpe_ratio, x.expected_annualized_return), reverse=True)
    return ranked[:3]
