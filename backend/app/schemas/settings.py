from pydantic import BaseModel


class AppSettings(BaseModel):
    binance_api_key: str = ""
    binance_api_secret: str = ""
    oanda_api_key: str = ""
    cme_api_key: str = ""
    default_market: str = "crypto"
    default_timeframe: str = "1h"
    default_assets: list[str] = ["BTCUSDT", "ETHUSDT"]


class AppSettingsUpdate(BaseModel):
    binance_api_key: str | None = None
    binance_api_secret: str | None = None
    oanda_api_key: str | None = None
    cme_api_key: str | None = None
    default_market: str | None = None
    default_timeframe: str | None = None
    default_assets: list[str] | None = None
