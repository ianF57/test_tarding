from typing import Literal

from pydantic import BaseModel, Field


MarketType = Literal["crypto", "forex", "futures"]
TimeFrame = Literal["1m", "5m", "1h", "1d", "1w"]


class StrategyPerformance(BaseModel):
    name: str
    expected_annualized_return: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    win_rate: float
    profit_factor: float
    suggested_direction: Literal["long", "short", "neutral"]
    confidence_score: float = Field(ge=0, le=100)
    favorable_conditions: str


class AssetRecommendation(BaseModel):
    asset: str
    market: MarketType
    timeframe: TimeFrame
    detected_regime: str
    top_strategies: list[StrategyPerformance]


class RecommendationRequest(BaseModel):
    assets: list[str]
    market: MarketType
    timeframe: TimeFrame = "1h"
    lookback_bars: int = 500
