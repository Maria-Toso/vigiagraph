from datetime import UTC, datetime

from app.domain.models import RiskAssessment, RiskLevel, RuleHit, Transaction
from app.infrastructure.repository import TransactionRepository


def test_repository_round_trip(tmp_path) -> None:
    repository = TransactionRepository(str(tmp_path / "test.db"))
    repository.initialize()
    item = Transaction(
        transaction_id="tx-001",
        user_id="user-001",
        card_id="card-001",
        device_id="device-001",
        ip_address="192.0.2.1",
        merchant_id="merchant-001",
        amount=6_000,
        occurred_at=datetime(2026, 8, 19, 15, tzinfo=UTC),
    )
    assessment = RiskAssessment(
        transaction_id=item.transaction_id,
        score=25,
        level=RiskLevel.LOW,
        triggered_rules=(RuleHit("HIGH_AMOUNT", "High amount", 25, {"amount": 6_000}),),
    )

    repository.save(item, assessment)

    stored = repository.get("tx-001")
    assert stored is not None
    assert stored["risk_score"] == 25
    assert stored["triggered_rules"][0]["code"] == "HIGH_AMOUNT"


def test_empty_summary(tmp_path) -> None:
    repository = TransactionRepository(str(tmp_path / "empty.db"))
    repository.initialize()

    assert repository.summary() == {
        "total_transactions": 0,
        "flagged_transactions": 0,
        "critical_transactions": 0,
        "average_risk_score": 0,
        "risk_distribution": {"low": 0, "medium": 0, "high": 0, "critical": 0},
        "top_rules": [],
    }
