from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import optuna
import pandas as pd

from app.strategies.indicators import atr, bollinger, ema, macd, obv, rsi, sma, stochastic


@dataclass
class StrategySpec:
    name: str
    params: dict
    style: str


def base_strategies() -> list[StrategySpec]:
    return [
        StrategySpec("ema_trend_rsi", {"fast": 20, "slow": 50, "rsi_low": 45, "rsi_high": 55}, "swing"),
        StrategySpec("macd_stoch", {"stoch_low": 20, "stoch_high": 80}, "intraday"),
        StrategySpec("bollinger_reversion", {"window": 20, "std": 2.0}, "intraday"),
        StrategySpec("sma_atr_breakout", {"sma_window": 50, "atr_window": 14, "atr_mult": 1.5}, "swing"),
        StrategySpec("obv_trend_confirm", {"ma_window": 20}, "intraday"),
    ]


def generate_signals(df: pd.DataFrame, spec: StrategySpec) -> pd.Series:
    close, high, low, volume = df["close"], df["high"], df["low"], df["volume"]

    if spec.name == "ema_trend_rsi":
        fast = ema(close, spec.params["fast"])
        slow = ema(close, spec.params["slow"])
        rsi_val = rsi(close)
        return pd.Series(
            np.where(
                (fast > slow) & (rsi_val > spec.params["rsi_high"]),
                1,
                np.where((fast < slow) & (rsi_val < spec.params["rsi_low"]), -1, 0),
            ),
            index=df.index,
        )

    if spec.name == "macd_stoch":
        macd_line, signal = macd(close)
        stoch = stochastic(high, low, close)
        return pd.Series(
            np.where(
                (macd_line > signal) & (stoch < spec.params["stoch_low"]),
                1,
                np.where((macd_line < signal) & (stoch > spec.params["stoch_high"]), -1, 0),
            ),
            index=df.index,
        )

    if spec.name == "bollinger_reversion":
        upper, lower = bollinger(close, spec.params["window"], spec.params["std"])
        return pd.Series(np.where(close < lower, 1, np.where(close > upper, -1, 0)), index=df.index)

    if spec.name == "obv_trend_confirm":
        obv_line = obv(close, volume)
        obv_ma = obv_line.rolling(spec.params["ma_window"]).mean()
        trend = ema(close, 20) - ema(close, 50)
        return pd.Series(np.where((obv_line > obv_ma) & (trend > 0), 1, np.where((obv_line < obv_ma) & (trend < 0), -1, 0)), index=df.index)

    base = sma(close, spec.params["sma_window"])
    a = atr(high, low, close, spec.params["atr_window"])
    return pd.Series(
        np.where(close > (base + spec.params["atr_mult"] * a), 1, np.where(close < (base - spec.params["atr_mult"] * a), -1, 0)),
        index=df.index,
    )


def optimize_parameters(df: pd.DataFrame, spec: StrategySpec, score_fn, n_trials: int = 20) -> StrategySpec:
    if spec.name not in {"ema_trend_rsi", "bollinger_reversion", "obv_trend_confirm"}:
        return spec

    def objective(trial: optuna.Trial) -> float:
        params = spec.params.copy()
        if spec.name == "ema_trend_rsi":
            params["fast"] = trial.suggest_int("fast", 5, 30)
            params["slow"] = trial.suggest_int("slow", 31, 120)
            params["rsi_low"] = trial.suggest_int("rsi_low", 30, 49)
            params["rsi_high"] = trial.suggest_int("rsi_high", 51, 70)
        if spec.name == "bollinger_reversion":
            params["window"] = trial.suggest_int("window", 10, 40)
            params["std"] = trial.suggest_float("std", 1.2, 3.0)
        if spec.name == "obv_trend_confirm":
            params["ma_window"] = trial.suggest_int("ma_window", 5, 40)
        trial_spec = StrategySpec(spec.name, params, spec.style)
        return score_fn(generate_signals(df, trial_spec))

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    final_params = spec.params | study.best_params
    return StrategySpec(spec.name, final_params, spec.style)
