from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException

from app.data.connectors import get_connector
from app.regime.detector import detect_regime
from app.recommendation.engine import recommend
from app.schemas.models import AssetRecommendation, RecommendationRequest
from app.strategies.generator import base_strategies, optimize_parameters

router = APIRouter(prefix="/api", tags=["research"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.post("/recommendations", response_model=list[AssetRecommendation])
async def recommendations(payload: RecommendationRequest) -> list[AssetRecommendation]:
    connector = get_connector(payload.market)
    specs = base_strategies()

    fetch_jobs = [connector.fetch_ohlcv(asset, payload.timeframe, payload.lookback_bars) for asset in payload.assets]
    fetched = await asyncio.gather(*fetch_jobs, return_exceptions=True)

    out: list[AssetRecommendation] = []
    for asset, result in zip(payload.assets, fetched, strict=True):
        if isinstance(result, Exception):
            raise HTTPException(status_code=400, detail=f"Failed to load {asset}: {result}") from result

        df = result
        if df.empty:
            raise HTTPException(status_code=400, detail=f"No data for {asset}")

        def objective(signal):
            returns = signal.shift(1).fillna(0) * df["close"].pct_change().fillna(0)
            return float(returns.mean() / (returns.std() + 1e-9))

        optimized_specs = [optimize_parameters(df, spec, objective, n_trials=10) for spec in specs]
        regime = detect_regime(df)
        top = recommend(df, payload.timeframe, regime, optimized_specs)
        out.append(
            AssetRecommendation(
                asset=asset,
                market=payload.market,
                timeframe=payload.timeframe,
                detected_regime=regime,
                top_strategies=top,
            )
        )

    return out
