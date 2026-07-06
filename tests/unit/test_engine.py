import pytest
from pydantic import ValidationError

from farmflow.engine import assess_scenario, percentile_value
from farmflow.fixtures import load_contract
from farmflow.models import DecisionStatus


def test_percentile_uses_linear_interpolation() -> None:
    values = [40, 50, 60, 70, 80, 90, 100, 110, 120, 130]
    assert percentile_value(values, 20) == 58


def test_all_four_demo_statuses() -> None:
    expected = {
        "demo_normal": DecisionStatus.NORMAL,
        "demo_watchlist": DecisionStatus.WATCHLIST,
        "demo_triggered": DecisionStatus.TRIGGERED_REVIEW,
        "demo_insufficient": DecisionStatus.INSUFFICIENT_DATA,
    }
    assert {
        contract_id: assess_scenario(contract_id).status
        for contract_id in expected
    } == expected


def test_rainfall_coverage_detects_missing_observations() -> None:
    result = assess_scenario("demo_insufficient")
    assert result.rainfall_coverage_percent == 80
    assert "below the contract minimum" in result.limitations[-1]


def test_ndvi_confirmation_is_deterministic() -> None:
    triggered = assess_scenario("demo_triggered")
    watchlist = assess_scenario("demo_watchlist")
    assert triggered.ndvi_anomaly == -0.2
    assert watchlist.ndvi_anomaly == -0.046


def test_contract_is_immutable() -> None:
    contract = load_contract()
    with pytest.raises(ValidationError):
        contract.mode = "production"  # type: ignore[misc]
