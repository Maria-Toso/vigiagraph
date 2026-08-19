from __future__ import annotations

import argparse

from app.config import settings
from app.infrastructure.repository import TransactionRepository
from app.services.demo_generator import generate_transactions
from app.services.risk_engine import RiskEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Populate VigiaGraph with synthetic data.")
    parser.add_argument("--count", type=int, default=80)
    parser.add_argument("--fraud-ratio", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    repository = TransactionRepository(settings.database_path)
    repository.initialize()
    engine = RiskEngine(high_amount_threshold=settings.high_amount_threshold)
    for transaction in generate_transactions(args.count, args.fraud_ratio, seed=args.seed):
        assessment = engine.assess(transaction, repository.history())
        repository.save(transaction, assessment)

    summary = repository.summary()
    print(f"Created {args.count} transactions")
    print(f"Flagged: {summary['flagged_transactions']}")
    print(f"Critical: {summary['critical_transactions']}")


if __name__ == "__main__":
    main()

