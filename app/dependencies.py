from __future__ import annotations

from functools import lru_cache

from app.config import settings
from app.infrastructure.repository import TransactionRepository
from app.services.risk_engine import RiskEngine


@lru_cache
def get_repository() -> TransactionRepository:
    repository = TransactionRepository(settings.database_path)
    repository.initialize()
    return repository


@lru_cache
def get_risk_engine() -> RiskEngine:
    return RiskEngine(
        high_amount_threshold=settings.high_amount_threshold,
        rapid_window_minutes=settings.rapid_window_minutes,
        rapid_transaction_limit=settings.rapid_transaction_limit,
    )

