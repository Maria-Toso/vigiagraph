from pathlib import Path

from fastapi.testclient import TestClient

from app.dependencies import get_repository
from app.infrastructure.repository import TransactionRepository
from app.main import app


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_transaction_endpoint(tmp_path: Path) -> None:
    repository = TransactionRepository(str(tmp_path / "api.db"))
    repository.initialize()
    app.dependency_overrides[get_repository] = lambda: repository
    payload = {
        "transaction_id": "tx-api-001",
        "user_id": "user-001",
        "card_id": "card-001",
        "device_id": "device-001",
        "ip_address": "192.0.2.1",
        "merchant_id": "merchant-001",
        "amount": 7500,
        "occurred_at": "2026-08-19T15:00:00Z",
    }

    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/transactions/analyze", json=payload)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["score"] == 25
    assert response.json()["triggered_rules"][0]["code"] == "HIGH_AMOUNT"

