from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.domain.models import Transaction

MERCHANTS = ("market-01", "fuel-02", "games-03", "travel-04", "food-05")
COUNTRIES = ("BR", "BR", "BR", "AR", "US")


def generate_transactions(
    count: int = 50,
    fraud_ratio: float = 0.2,
    *,
    seed: int | None = None,
) -> list[Transaction]:
    """Create reproducible synthetic data without using real financial information."""
    if not 1 <= count <= 1_000:
        raise ValueError("count must be between 1 and 1000")
    if not 0 <= fraud_ratio <= 1:
        raise ValueError("fraud_ratio must be between 0 and 1")

    rng = random.Random(seed)
    base_time = datetime.now(UTC).replace(hour=8, minute=0, second=0, microsecond=0) - timedelta(
        days=1
    )
    suspicious_device = "device-shared-risk"
    suspicious_ip = "198.51.100.42"
    transactions: list[Transaction] = []

    for index in range(count):
        user_number = rng.randint(1, 12)
        card_number = user_number * 10 + rng.randint(1, 2)
        suspicious = rng.random() < fraud_ratio
        occurred_at = base_time + timedelta(minutes=index * 7 + rng.randint(0, 4))

        if suspicious:
            amount = round(rng.uniform(5_500, 12_000), 2)
            device_id = suspicious_device
            ip_address = suspicious_ip
            country = rng.choice(("US", "RU", "AR"))
            if rng.random() < 0.35:
                occurred_at = occurred_at.replace(hour=rng.randint(0, 4))
        else:
            amount = round(rng.lognormvariate(4.2, 0.6), 2)
            device_id = f"device-{user_number:03d}"
            ip_address = f"192.0.2.{user_number}"
            country = rng.choice(COUNTRIES[:3])

        transactions.append(
            Transaction(
                transaction_id=str(uuid4()),
                user_id=f"user-{user_number:03d}",
                card_id=f"card-{card_number:04d}",
                device_id=device_id,
                ip_address=ip_address,
                merchant_id=rng.choice(MERCHANTS),
                amount=amount,
                occurred_at=occurred_at,
                country=country,
                channel=rng.choice(("online", "pos", "wallet")),
            )
        )

    return sorted(transactions, key=lambda item: item.normalized_datetime())
