from __future__ import annotations

import json
import sqlite3
from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.domain.models import RiskAssessment, Transaction


class TransactionRepository:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        path = Path(self.database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    card_id TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    merchant_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    occurred_at TEXT NOT NULL,
                    country TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    risk_score INTEGER NOT NULL,
                    risk_level TEXT NOT NULL,
                    triggered_rules TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_transactions_card ON transactions(card_id)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_transactions_risk ON transactions(risk_score)"
            )

    def save(self, transaction: Transaction, assessment: RiskAssessment) -> None:
        rules = [
            {
                "code": hit.code,
                "description": hit.description,
                "weight": hit.weight,
                "evidence": hit.evidence,
            }
            for hit in assessment.triggered_rules
        ]
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO transactions (
                    transaction_id, user_id, card_id, device_id, ip_address,
                    merchant_id, amount, occurred_at, country, currency, channel,
                    latitude, longitude, risk_score, risk_level, triggered_rules
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    transaction.transaction_id,
                    transaction.user_id,
                    transaction.card_id,
                    transaction.device_id,
                    transaction.ip_address,
                    transaction.merchant_id,
                    transaction.amount,
                    transaction.normalized_datetime().isoformat(),
                    transaction.country,
                    transaction.currency,
                    transaction.channel,
                    transaction.latitude,
                    transaction.longitude,
                    assessment.score,
                    assessment.level.value,
                    json.dumps(rules),
                ),
            )

    def history(self, limit: int = 1_000) -> list[Transaction]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM transactions ORDER BY occurred_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._row_to_transaction(row) for row in rows]

    def list(self, *, limit: int = 100, min_score: int = 0) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM transactions
                WHERE risk_score >= ?
                ORDER BY occurred_at DESC
                LIMIT ?
                """,
                (min_score, limit),
            ).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get(self, transaction_id: str) -> dict[str, object] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,)
            ).fetchone()
        return self._row_to_dict(row) if row else None

    def summary(self) -> dict[str, object]:
        with self._connect() as connection:
            totals = connection.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    COALESCE(AVG(risk_score), 0) AS average,
                    COALESCE(
                        SUM(CASE WHEN risk_level IN ('high', 'critical') THEN 1 ELSE 0 END),
                        0
                    ) AS flagged,
                    COALESCE(
                        SUM(CASE WHEN risk_level = 'critical' THEN 1 ELSE 0 END),
                        0
                    ) AS critical
                FROM transactions
                """
            ).fetchone()
            levels = connection.execute(
                "SELECT risk_level, COUNT(*) AS count FROM transactions GROUP BY risk_level"
            ).fetchall()
            rule_rows = connection.execute("SELECT triggered_rules FROM transactions").fetchall()

        level_counts = Counter({row["risk_level"]: row["count"] for row in levels})
        rule_counts: Counter[str] = Counter()
        for row in rule_rows:
            rule_counts.update(rule["code"] for rule in json.loads(row["triggered_rules"]))

        return {
            "total_transactions": totals["total"],
            "flagged_transactions": totals["flagged"],
            "critical_transactions": totals["critical"],
            "average_risk_score": round(totals["average"], 1),
            "risk_distribution": {
                level: level_counts[level] for level in ("low", "medium", "high", "critical")
            },
            "top_rules": [
                {"code": code, "count": count} for code, count in rule_counts.most_common(5)
            ],
        }

    @staticmethod
    def _row_to_transaction(row: sqlite3.Row) -> Transaction:
        from datetime import datetime

        return Transaction(
            transaction_id=row["transaction_id"],
            user_id=row["user_id"],
            card_id=row["card_id"],
            device_id=row["device_id"],
            ip_address=row["ip_address"],
            merchant_id=row["merchant_id"],
            amount=row["amount"],
            occurred_at=datetime.fromisoformat(row["occurred_at"]),
            country=row["country"],
            currency=row["currency"],
            channel=row["channel"],
            latitude=row["latitude"],
            longitude=row["longitude"],
        )

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict[str, object]:
        record = dict(row)
        record["triggered_rules"] = json.loads(record["triggered_rules"])
        return record
