from datetime import UTC, datetime, timedelta

from app.domain.models import RiskLevel, Transaction
from app.services.risk_engine import RiskEngine

NOW = datetime(2026, 8, 19, 14, 0, tzinfo=UTC)


def transaction(
    suffix: str,
    *,
    user_id: str = "user-001",
    card_id: str = "card-001",
    device_id: str = "device-001",
    ip_address: str = "192.0.2.1",
    amount: float = 100,
    occurred_at: datetime = NOW,
    country: str = "BR",
) -> Transaction:
    return Transaction(
        transaction_id=f"tx-{suffix}",
        user_id=user_id,
        card_id=card_id,
        device_id=device_id,
        ip_address=ip_address,
        merchant_id="merchant-001",
        amount=amount,
        occurred_at=occurred_at,
        country=country,
    )


def test_normal_transaction_has_low_risk() -> None:
    result = RiskEngine().assess(transaction("normal"))

    assert result.score == 0
    assert result.level is RiskLevel.LOW
    assert result.triggered_rules == ()


def test_high_amount_rule_is_explainable() -> None:
    result = RiskEngine().assess(transaction("high", amount=7_500))

    assert result.score == 25
    assert result.triggered_rules[0].code == "HIGH_AMOUNT"
    assert result.triggered_rules[0].evidence["amount"] == 7_500


def test_multiple_signals_create_critical_risk() -> None:
    history = [
        transaction(
            str(index),
            user_id=f"user-{index + 2:03d}",
            card_id="card-001",
            device_id="shared-device",
            occurred_at=NOW - timedelta(minutes=index + 1),
        )
        for index in range(3)
    ]
    current = transaction(
        "critical",
        amount=9_000,
        device_id="shared-device",
        occurred_at=NOW,
    )

    result = RiskEngine().assess(current, history)
    codes = {hit.code for hit in result.triggered_rules}

    assert result.score == 100
    assert result.level is RiskLevel.CRITICAL
    assert {"HIGH_AMOUNT", "RAPID_SUCCESSION", "SHARED_DEVICE", "AMOUNT_ANOMALY"} <= codes


def test_country_change_needs_a_stable_baseline() -> None:
    history = [
        transaction(str(index), occurred_at=NOW - timedelta(days=index + 1), country="BR")
        for index in range(3)
    ]

    result = RiskEngine().assess(transaction("abroad", country="US"), history)

    assert any(hit.code == "COUNTRY_CHANGE" for hit in result.triggered_rules)

