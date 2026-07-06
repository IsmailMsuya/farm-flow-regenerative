from __future__ import annotations

from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from farmflow.fixtures import list_portfolio
from farmflow.models import ReviewOutcome
from farmflow.policy import check_policy
from farmflow.workflow import build_response

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"

api = FastAPI(
    title="Farm Flow Regenerative",
    description="Simulation-only climate-relief decision-support prototype",
    version="0.1.0",
)
api.mount("/assets", StaticFiles(directory=FRONTEND), name="assets")


class PolicyRequest(BaseModel):
    intent: str


class ReviewerOutcomeRequest(BaseModel):
    outcome: ReviewOutcome


@api.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND / "index.html")


@api.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "simulation_only"}


@api.get("/api/contracts")
def contracts() -> list[dict[str, object]]:
    return list_portfolio()


@api.get("/api/assessments/{contract_id}")
def assessment(contract_id: str) -> dict[str, object]:
    try:
        return build_response(contract_id).model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@api.post("/api/policy/check")
def policy_check(request: PolicyRequest) -> dict[str, object]:
    return check_policy(request.intent).model_dump(mode="json")


@api.post("/api/assessments/{contract_id}/review-outcome")
def review_outcome(
    contract_id: str,
    request: ReviewerOutcomeRequest,
) -> dict[str, object]:
    try:
        response = build_response(contract_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "recorded_for_demo": True,
        "contract_id": contract_id,
        "assessment_id": response.assessment.assessment_id,
        "outcome": request.outcome.value,
        "financial_record_changed": False,
        "message": "Simulated reviewer outcome acknowledged in memory only.",
    }


def main() -> None:
    uvicorn.run("farmflow.api:api", host="0.0.0.0", port=8080, reload=False)


if __name__ == "__main__":
    main()

