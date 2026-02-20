from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Trading Research & Strategy Automation"
    default_assets: list[str] = ["BTCUSDT", "EUR_USD", "ES1!"]
    default_timeframes: list[str] = ["1m", "5m", "1h", "1d", "1w"]
    transaction_cost_bps: float = 5.0
    slippage_bps: float = 2.0


settings = Settings()
