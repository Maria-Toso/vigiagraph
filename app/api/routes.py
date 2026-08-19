from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_repository, get_risk_engine
from app.infrastructure.repository import TransactionRepository
from app.schemas import AssessmentResponse, DemoRequest, TransactionCreate
from app.services.demo_generator import generate_transactions
from app.services.risk_engine import RiskEngine

router = APIRouter(prefix="/api/v1")
RepositoryDep = Annotated[TransactionRepository, Depends(get_repository)]
RiskEngineDep = Annotated[RiskEngine, Depends(get_risk_engine)]


@router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "vigiagraph"}


@router.post(
    "/transactions/analyze",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["transactions"],
)
def analyze_transaction(
    payload: TransactionCreate,
    repository: RepositoryDep,
    engine: RiskEngineDep,
) -> AssessmentResponse:
    transaction = payload.to_domain()
    assessment = engine.assess(transaction, repository.history())
    repository.save(transaction, assessment)
    return AssessmentResponse(
        transaction_id=assessment.transaction_id,
        score=assessment.score,
        level=assessment.level.value,
        triggered_rules=[
            {
                "code": hit.code,
                "description": hit.description,
                "weight": hit.weight,
                "evidence": hit.evidence,
            }
            for hit in assessment.triggered_rules
        ],
    )


@router.get("/transactions", tags=["transactions"])
def list_transactions(
    repository: RepositoryDep,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    min_score: Annotated[int, Query(ge=0, le=100)] = 0,
) -> list[dict[str, object]]:
    return repository.list(limit=limit, min_score=min_score)


@router.get("/transactions/{transaction_id}", tags=["transactions"])
def get_transaction(
    transaction_id: str,
    repository: RepositoryDep,
) -> dict[str, object]:
    transaction = repository.get(transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.get("/dashboard/summary", tags=["dashboard"])
def dashboard_summary(
    repository: RepositoryDep,
) -> dict[str, object]:
    return repository.summary()


@router.post("/demo/generate", status_code=status.HTTP_201_CREATED, tags=["demo"])
def generate_demo_data(
    payload: DemoRequest,
    repository: RepositoryDep,
    engine: RiskEngineDep,
) -> dict[str, object]:
    transactions = generate_transactions(
        count=payload.count,
        fraud_ratio=payload.fraud_ratio,
        seed=payload.seed,
    )
    for transaction in transactions:
        assessment = engine.assess(transaction, repository.history())
        repository.save(transaction, assessment)
    return {"created": len(transactions), "summary": repository.summary()}
