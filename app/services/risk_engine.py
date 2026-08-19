from __future__ import annotations

from collections import Counter
from datetime import timedelta
from statistics import fmean

from app.domain.models import RiskAssessment, RiskLevel, RuleHit, Transaction


class RiskEngine:
    """Scores a transaction using deterministic and explainable rules."""

    def __init__(
        self,
        *,
        high_amount_threshold: float = 5_000,
        rapid_window_minutes: int = 5,
        rapid_transaction_limit: int = 3,
    ) -> None:
        self.high_amount_threshold = high_amount_threshold
        self.rapid_window = timedelta(minutes=rapid_window_minutes)
        self.rapid_transaction_limit = rapid_transaction_limit

    def assess(
        self, transaction: Transaction, history: list[Transaction] | None = None
    ) -> RiskAssessment:
        history = history or []
        hits: list[RuleHit] = []

        self._check_high_amount(transaction, hits)
        self._check_odd_hours(transaction, hits)
        self._check_rapid_succession(transaction, history, hits)
        self._check_shared_device(transaction, history, hits)
        self._check_shared_ip(transaction, history, hits)
        self._check_amount_anomaly(transaction, history, hits)
        self._check_country_change(transaction, history, hits)

        score = min(sum(hit.weight for hit in hits), 100)
        return RiskAssessment(
            transaction_id=transaction.transaction_id,
            score=score,
            level=self._level_for(score),
            triggered_rules=tuple(hits),
        )

    def _check_high_amount(self, transaction: Transaction, hits: list[RuleHit]) -> None:
        if transaction.amount >= self.high_amount_threshold:
            hits.append(
                RuleHit(
                    code="HIGH_AMOUNT",
                    description="Valor acima do limite configurado.",
                    weight=25,
                    evidence={
                        "amount": round(transaction.amount, 2),
                        "threshold": self.high_amount_threshold,
                    },
                )
            )

    @staticmethod
    def _check_odd_hours(transaction: Transaction, hits: list[RuleHit]) -> None:
        hour = transaction.normalized_datetime().hour
        if 0 <= hour < 5:
            hits.append(
                RuleHit(
                    code="ODD_HOURS",
                    description="Transacao realizada em horario incomum.",
                    weight=10,
                    evidence={"utc_hour": hour},
                )
            )

    def _check_rapid_succession(
        self,
        transaction: Transaction,
        history: list[Transaction],
        hits: list[RuleHit],
    ) -> None:
        current_time = transaction.normalized_datetime()
        recent = [
            item
            for item in history
            if item.card_id == transaction.card_id
            and timedelta(0)
            <= current_time - item.normalized_datetime()
            <= self.rapid_window
        ]
        if len(recent) >= self.rapid_transaction_limit:
            hits.append(
                RuleHit(
                    code="RAPID_SUCCESSION",
                    description="Muitas transacoes do mesmo cartao em poucos minutos.",
                    weight=35,
                    evidence={
                        "previous_transactions": len(recent),
                        "window_minutes": int(self.rapid_window.total_seconds() / 60),
                    },
                )
            )

    @staticmethod
    def _check_shared_device(
        transaction: Transaction,
        history: list[Transaction],
        hits: list[RuleHit],
    ) -> None:
        users = {item.user_id for item in history if item.device_id == transaction.device_id}
        users.discard(transaction.user_id)
        if users:
            hits.append(
                RuleHit(
                    code="SHARED_DEVICE",
                    description="Dispositivo associado a outros usuarios.",
                    weight=30,
                    evidence={"other_users": len(users)},
                )
            )

    @staticmethod
    def _check_shared_ip(
        transaction: Transaction,
        history: list[Transaction],
        hits: list[RuleHit],
    ) -> None:
        cards = {item.card_id for item in history if item.ip_address == transaction.ip_address}
        cards.discard(transaction.card_id)
        if len(cards) >= 3:
            hits.append(
                RuleHit(
                    code="SHARED_IP",
                    description="Endereco IP associado a varios cartoes.",
                    weight=25,
                    evidence={"other_cards": len(cards)},
                )
            )

    @staticmethod
    def _check_amount_anomaly(
        transaction: Transaction,
        history: list[Transaction],
        hits: list[RuleHit],
    ) -> None:
        amounts = [item.amount for item in history if item.card_id == transaction.card_id]
        if len(amounts) < 3:
            return
        average = fmean(amounts)
        threshold = max(200.0, average * 4)
        if transaction.amount >= threshold:
            hits.append(
                RuleHit(
                    code="AMOUNT_ANOMALY",
                    description="Valor muito acima do historico deste cartao.",
                    weight=25,
                    evidence={
                        "amount": round(transaction.amount, 2),
                        "historical_average": round(average, 2),
                    },
                )
            )

    @staticmethod
    def _check_country_change(
        transaction: Transaction,
        history: list[Transaction],
        hits: list[RuleHit],
    ) -> None:
        countries = [item.country for item in history if item.user_id == transaction.user_id]
        if len(countries) < 3:
            return
        baseline, occurrences = Counter(countries).most_common(1)[0]
        if occurrences >= 3 and transaction.country != baseline:
            hits.append(
                RuleHit(
                    code="COUNTRY_CHANGE",
                    description="Pais diferente do padrao recente do usuario.",
                    weight=15,
                    evidence={"current_country": transaction.country, "usual_country": baseline},
                )
            )

    @staticmethod
    def _level_for(score: int) -> RiskLevel:
        if score >= 80:
            return RiskLevel.CRITICAL
        if score >= 60:
            return RiskLevel.HIGH
        if score >= 30:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

