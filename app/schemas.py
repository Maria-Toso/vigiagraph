from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.domain.models import Transaction


class TransactionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    transaction_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str = Field(min_length=1, max_length=80)
    card_id: str = Field(min_length=1, max_length=80)
    device_id: str = Field(min_length=1, max_length=80)
    ip_address: str = Field(min_length=3, max_length=64)
    merchant_id: str = Field(min_length=1, max_length=80)
    amount: float = Field(gt=0, le=10_000_000)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    country: str = Field(default="BR", min_length=2, max_length=2)
    currency: str = Field(default="BRL", min_length=3, max_length=3)
    channel: str = Field(default="online", min_length=1, max_length=30)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    def to_domain(self) -> Transaction:
        return Transaction(**self.model_dump())


class RuleHitResponse(BaseModel):
    code: str
    description: str
    weight: int
    evidence: dict[str, object]


class AssessmentResponse(BaseModel):
    transaction_id: str
    score: int
    level: str
    triggered_rules: list[RuleHitResponse]


class DemoRequest(BaseModel):
    count: int = Field(default=50, ge=1, le=500)
    fraud_ratio: float = Field(default=0.2, ge=0, le=1)
    seed: int | None = None

