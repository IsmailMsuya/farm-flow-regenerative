from fastapi.testclient import TestClient

from farmflow.api import api

client = TestClient(api)


def test_health_and_portfolio() -> None:
    assert client.get("/health").json() == {
        "status": "ok",
        "mode": "simulation_only",
    }
    contracts = client.get("/api/contracts").json()
    assert len(contracts) == 4


def test_triggered_review_response() -> None:
    response = client.get("/api/assessments/demo_triggered")
    assert response.status_code == 200
    body = response.json()
    assert body["assessment"]["status"] == "triggered_review"
    assert body["packet"]["requires_human_review"] is True


def test_unknown_contract_is_rejected() -> None:
    assert client.get("/api/assessments/real-borrower-123").status_code == 404


def test_reviewer_outcome_never_changes_financial_record() -> None:
    response = client.post(
        "/api/assessments/demo_triggered/review-outcome",
        json={"outcome": "approved_for_follow_up"},
    )
    assert response.status_code == 200
    assert response.json()["financial_record_changed"] is False

