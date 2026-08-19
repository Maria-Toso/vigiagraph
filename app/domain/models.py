from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class Transaction:
    transaction_id: str
    user_id: str
    card_id: str
    device_id: str
    ip_address: str
    merchant_id: str
    amount: float
    occurred_at: datetime
    country: str = "BR"
    currency: str = "BRL"
    channel: str = "online"
    latitude: float | None = None
    longitude: float | None = None

    def normalized_datetime(self) -> datetime:
        if self.occurred_at.tzinfo is None:
            return self.occurred_at.replace(tzinfo=UTC)
        return self.occurred_at.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class RuleHit:
    code: str
    description: str
    weight: int
    evidence: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RiskAssessment:
    transaction_id: str
    score: int
    level: RiskLevel
    triggered_rules: tuple[RuleHit, ...]

