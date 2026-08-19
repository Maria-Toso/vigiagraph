from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "VigiaGraph")
    app_env: str = os.getenv("APP_ENV", "development")
    database_path: str = os.getenv("DATABASE_PATH", "./data/vigiagraph.db")
    high_amount_threshold: float = float(os.getenv("HIGH_AMOUNT_THRESHOLD", "5000"))
    rapid_window_minutes: int = int(os.getenv("RAPID_WINDOW_MINUTES", "5"))
    rapid_transaction_limit: int = int(os.getenv("RAPID_TRANSACTION_LIMIT", "3"))


settings = Settings()

