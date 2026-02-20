from __future__ import annotations

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "local_state.db"

DEFAULT_SETTINGS = {
    "binance_api_key": "",
    "binance_api_secret": "",
    "oanda_api_key": "",
    "cme_api_key": "",
    "default_market": "crypto",
    "default_timeframe": "1h",
    "default_assets": ["BTCUSDT", "ETHUSDT"],
}


class SettingsStore:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            conn.commit()
        self.seed_defaults()

    def seed_defaults(self) -> None:
        current = self.get_all()
        missing = {k: v for k, v in DEFAULT_SETTINGS.items() if k not in current}
        if not missing:
            return
        self.update_many(missing)

    def get_all(self) -> dict:
        with self._connect() as conn:
            rows = conn.execute("SELECT key, value FROM app_settings").fetchall()
        out = {}
        for key, value in rows:
            try:
                out[key] = json.loads(value)
            except json.JSONDecodeError:
                out[key] = value
        return out

    def update_many(self, updates: dict) -> dict:
        with self._connect() as conn:
            for key, value in updates.items():
                conn.execute(
                    "INSERT INTO app_settings(key, value) VALUES(?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                    (key, json.dumps(value)),
                )
            conn.commit()
        return self.get_all()


store = SettingsStore()
