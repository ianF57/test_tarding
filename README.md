# Trading Research & Strategy Automation

Full-stack app for strategy generation, backtesting, market regime detection, and strategy recommendation across crypto, forex, and futures.

## Stack
- Backend: FastAPI, Pandas, NumPy, scikit-learn, Optuna
- Frontend: Next.js + React + Chart.js
- Database: PostgreSQL (compose service ready)
- Data connectors: Binance live REST + pluggable connectors (Oanda/CME scaffold)

## What this app does
For each requested asset/timeframe, the backend returns:
- Current detected market regime
- Top 3 ranked strategies
- Expected annualized return
- Max drawdown
- Suggested trade direction (long/short/neutral)
- Confidence score (0-100)

## Implemented features
- Rule-based strategy generation using EMA/SMA/MACD/RSI/Stochastic/ATR/Bollinger and a volume-based OBV strategy.
- Parameter optimization with Optuna for selected strategies.
- Backtesting with transaction costs, slippage, position sizing, and metrics:
  - CAGR, Sharpe, Sortino, Max Drawdown, Win Rate, Profit Factor.
- Market regime detection:
  - trending vs ranging and high-vol vs low-vol via ADX + rolling volatility clustering (KMeans).
- Recommendation engine ranking by risk-adjusted profile and regime fit.
- Configurable timeframes: 1m, 5m, 1h, 1d, 1w.
- Async market data fetching for multiple assets per request.

## How to open and use this

### Option A (quickest): one command helper
```bash
./scripts/open_and_use.sh
```
Then open:
- Frontend dashboard: `http://localhost:3000`
- Backend docs (Swagger): `http://localhost:8000/docs`

### Option B: manual Docker Compose
```bash
docker compose up -d
```

Check health:
```bash
curl http://localhost:8000/api/health
```

Open UI:
- `http://localhost:3000`
- Click **Analyze Market**

Stop services:
```bash
docker compose down
```

## API example
```bash
curl -X POST http://localhost:8000/api/recommendations \
  -H 'Content-Type: application/json' \
  -d '{
    "assets": ["BTCUSDT", "ETHUSDT", "BNBUSDT"],
    "market": "crypto",
    "timeframe": "1h",
    "lookback_bars": 500
  }'
```

## Notes
- `market: crypto` uses Binance live data.
- `market: forex` and `market: futures` currently use synthetic fallback connectors unless real Oanda/CME connectors are wired.
- Live trade execution is intentionally out of scope for this version.
